import sys
import subprocess

from pathlib import Path

def run_make_binary():
    print("Running the binary script:")
    scripts_dir = Path(__file__).parent
    subprocess.run(
        [scripts_dir / "binary.sh"], stdout=sys.stdout, stderr=sys.stderr
    )
    return

if __name__ == "__main__":
    run_make_binary()
