import argparse
from pathlib import Path

def get_version():
    # Read the version from the VERSION file located one directory up
    version_file = Path(__file__).resolve().parent / "VERSION"
    with open(version_file) as f:
        return f.read().strip()

def main():
    parser = argparse.ArgumentParser(description="mloptimizer command line interface")
    parser.add_argument("--version", action="store_true", help="Show the installed version of mloptimizer")
    args = parser.parse_args()

    if args.version:
        version = get_version()
        print(f"mloptimizer version: {version}")
    else:
        # Run other main code or default actions here
        pass

if __name__ == "__main__":
    main()
