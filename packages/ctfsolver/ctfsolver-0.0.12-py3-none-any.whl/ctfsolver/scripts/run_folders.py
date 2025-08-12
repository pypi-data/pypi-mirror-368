import subprocess
import sys


def main():
    result = subprocess.run([sys.executable, "-m", "ctfsolver.folders"], check=True)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
