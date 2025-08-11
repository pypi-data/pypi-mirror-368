#!/usr/bin/env python3
import os
import sys
import glob
import yaml
import argparse
import tempfile
import subprocess
from pathlib import Path
from osgeo import ogr, gdal, osr

ogr.DontUseExceptions()
gdal.DontUseExceptions()
osr.DontUseExceptions()

# tiny helpers

def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def ensure_dir(p):
    Path(p).mkdir(parents=True, exist_ok=True)

def set_gdal_config(cfg):
    if not cfg:
        return
    for k, v in cfg.items():
        os.environ[str(k)] = str(v)

# geometry + blocks

def open_layer(path, layer_name=None):
    ds = ogr.Open(path, 0)
    if ds is None:
        raise ValueError(f"could not open: {path}")
    if layer_name is None:
        layer = ds.GetLayer(0)
    else:
        layer = ds.GetLayerByName(layer_name)
    if layer is None:
        raise ValueError(f"layer not found in {path}: {layer_name}")
    return ds, layer

def aoi_extent(aoi_path, aoi_layer=None):
    ds, layer = open_layer(aoi_path, aoi_layer)
    ext = layer.GetExtent()  # (minx, maxx, miny, maxy)
    ds = None
    return ext

def intersecting_blocks(blocks_path, id_field, bbox):
    drv = ogr.GetDriverByName("ESRI Shapefile")
    ds = drv.Open(blocks_path, 0)
    if ds is None:
        raise ValueError(f"could not open blocks: {blocks_path}")
    layer = ds.GetLayer()
    ws_min_x, ws_max_x, ws_min_y, ws_max_y = bbox
    ids = []
    for ft in layer:
        geom = ft.GetGeometryRef()
        if geom is None:
            continue
        bminx, bmaxx, bminy, bmaxy = geom.GetEnvelope()
        if (bmaxx >= ws_min_x and bminx <= ws_max_x and
            bmaxy >= ws_min_y and bminy <= ws_max_y):
            val = ft.GetField(id_field)
            if val is not None:
                ids.append(int(val))
    ds = None
    if not ids:
        raise ValueError("no intersecting blocks")
    return sorted(set(ids))

def read_block_list(path):
    with open(path, "r") as f:
        out = [int(s.strip()) for s in f if s.strip().isdigit()]
    if not out:
        raise ValueError(f"no valid block ids found: {path}")
    return sorted(set(out))

# launch gcn10

def run_gcn10(cfg, block_ids):
    tmp_dir = cfg["io"].get("tmp_dir", "./tmp")
    ensure_dir(tmp_dir)
    keep = bool(cfg["io"].get("keep_intermediate", False))
    # write block list (unless provided)
    block_list_path = cfg.get("block_list_path")
    created_tmp = False
    if block_list_path is None:
        fd, tmpname = tempfile.mkstemp(prefix="blocks_", suffix=".txt", dir=tmp_dir)
        os.close(fd)
        with open(tmpname, "w") as f:
            f.write("\n".join(map(str, block_ids)) + "\n")
        block_list_path = tmpname
        created_tmp = True

    use_api = bool(cfg["run"].get("use_api", False))
    overwrite = bool(cfg["run"].get("overwrite", False))
    config_path = cfg["run"]["gcn10_config"]

    if use_api:
        try:
            from gcn10py import run as gcn_run
        except Exception as e:
            raise RuntimeError(f"use_api=true but gcn10py not importable: {e}")
        args = ["-c", config_path, "-l", block_list_path]
        if overwrite:
            args.append("-o")
        print("running gcn10 via python api:", args)
        gcn_run(args)
    else:
        cli_cmd = cfg["run"].get("cli_cmd", "gcn10py")
        launcher = cfg["run"].get("launcher", "mpirun")
        nproc = int(cfg["run"].get("nproc", 1))
        launcher_args = list(cfg["run"].get("launcher_args", []))
        cmd = [launcher, "-n", str(nproc)] + launcher_args + [cli_cmd, "-c", config_path, "-l", block_list_path]
        if overwrite:
            cmd.append("-o")
        print("executing:", " ".join(cmd))
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.stdout:
            print(res.stdout, end="")
        if res.returncode != 0:
            if res.stderr:
                print(res.stderr, file=sys.stderr, end="")
            raise RuntimeError(f"gcn10 run failed with code {res.returncode}")

    if created_tmp and not keep and os.path.exists(block_list_path):
        try:
            os.remove(block_list_path)
        except OSError:
            pass

# mosaic + clip

#def find_rasters(base_dir_tmpl, glob_tmpl, drainage, hc, arc):
#    base = Path(base_dir_tmpl.format(drainage=drainage))
#    patt = glob_tmpl.format(drainage=drainage, hc=hc, arc=arc)
#    return sorted(glob.glob(str(base / patt)))
def find_rasters(base_dir_tmpl, glob_tmpl, drainage, hc, arc):
    base = Path(base_dir_tmpl.format(drainage=drainage))
    patterns = glob_tmpl if isinstance(glob_tmpl, list) else [glob_tmpl]
    out = []
    for patt in patterns:
        patt = patt.format(drainage=drainage, hc=hc, arc=arc)
        out.extend(glob.glob(str(base / patt)))
    return sorted(set(out))

def build_vrt(paths):
    if not paths:
        return None
    vrt = gdal.BuildVRT("", paths, separate=False)
    return vrt

def clip_to_aoi(vrt, aoi_path, out_path, dst_nodata, warp_opts):
    ensure_dir(Path(out_path).parent)
    kw = dict(format="GTiff", cutlineDSName=aoi_path, cropToCutline=True, dstNodata=dst_nodata)
    if warp_opts:
        kw.update(warp_opts)
    gdal.Warp(out_path, vrt, **kw)

# main

def main():
    p = argparse.ArgumentParser(description="yaml-driven gcn10 runner + mosaic + clip")
    p.add_argument("-y", "--yaml", required=True, help="path to yaml config")
    args = p.parse_args()

    cfg = load_yaml(args.yaml)
    set_gdal_config(cfg.get("gdal", {}).get("config"))

    aoi_cfg = cfg["aoi"]
    blocks_cfg = cfg["blocks"]
    combos = cfg.get("combos", {})
    hc_types = combos.get("hc_types", ["p", "f", "i"])
    arc_types = combos.get("arc_types", ["i", "ii", "iii"])
    drainage_types = combos.get("drainage_types", ["drained", "undrained"])

    out_dir = cfg["io"]["output_dir"]
    ensure_dir(out_dir)

    if cfg.get("block_ids"):
        block_ids = sorted(set(int(x) for x in cfg["block_ids"]))
    elif cfg.get("block_list_path"):
        block_ids = read_block_list(cfg["block_list_path"])
    else:
        bbox = aoi_extent(aoi_cfg["path"], aoi_cfg.get("layer"))
        block_ids = intersecting_blocks(blocks_cfg["path"], blocks_cfg.get("id_field", "ID"), bbox)

    print(f"blocks: {len(block_ids)}")

    run_gcn10(cfg, block_ids)

    dst_nodata = cfg.get("gdal", {}).get("dst_nodata", 0)
    warp_opts = cfg.get("gdal", {}).get("warp_options", {})

    base_dir_tmpl = cfg["mosaic"]["raster_dir_template"]
    glob_tmpl = cfg["mosaic"]["raster_glob_template"]
    out_tmpl = cfg["mosaic"]["output_filename_template"]

    for drainage in drainage_types:
        for hc in hc_types:
            for arc in arc_types:
                rasters = find_rasters(base_dir_tmpl, glob_tmpl, drainage, hc, arc)
                if not rasters:
                    print(f"no rasters for {drainage} {hc} {arc}")
                    continue
                print(f"merging {len(rasters)} rasters for {drainage}/{hc}/{arc}")
                vrt = build_vrt(rasters)
                if vrt is None:
                    print("skip: vrt build failed")
                    continue
                out_name = out_tmpl.format(drainage=drainage, hc=hc, arc=arc)
                out_path = str(Path(out_dir) / out_name)
                print(f"writing {out_path}")
                clip_to_aoi(vrt, aoi_cfg["path"], out_path, dst_nodata, warp_opts)
                vrt = None

if __name__ == "__main__":
    main()
