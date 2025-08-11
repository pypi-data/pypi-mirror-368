import subprocess
import sys
import os
import platform
from pathlib import Path

def get_executable_path():
    """return the path to the gcn10 executable, bundled with the package."""
    # get package directory
    package_dir = Path(__file__).parent

    # use platform-appropriate executable
    exe_name = "gcn10.exe" if platform.system() == "Windows" else "gcn10"
    exe_path = package_dir / exe_name
    # check if executable exists
    if not exe_path.is_file():
        raise FileNotFoundError(f"gcn10 executable not found at {exe_path}")

    # ensure executable permissions on unix systems
    if platform.system() != "Windows":
        os.chmod(exe_path, 0o755)
    return str(exe_path)

def run_gcn10(args=None):
    """
    run the gcn10 executable with the provided arguments.
    
    args:
        args (list): list of command-line arguments
        (e.g., ['-c', 'config.txt', '-l', 'block_ids.txt', '-o', 'overwrite']).
                     if none, uses sys.argv[1:].
    
    returns:
        subprocess.completedprocess: result of the gcn10 execution.
    
    raises:
        subprocess.calledprocesserror: if gcn10 returns a non-zero exit code.
        filenotfounderror: if the gcn10 executable is not found.
    """
    # use sys.argv if no args provided
    if args is None:
        args = sys.argv[1:]

    try:
        # get path to gcn10 executable
        exe_path = get_executable_path()

        # construct command with executable path and args
        cmd = [exe_path] + args

        # run gcn10, capture std. out and err
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        # print stdout
        if result.stdout:
            print(result.stdout, end="")

        # print stderr
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        return result
    except subprocess.CalledProcessError as e:
        
        # print err and re-raise
        print(f"error running gcn10: {e.stderr}", file=sys.stderr)
        raise
    except FileNotFoundError as e:

        # print err and re-raise
        print(f"error: {e}", file=sys.stderr)
        raise

if __name__ == "__main__":

    # run the main function
    run_gcn10()
