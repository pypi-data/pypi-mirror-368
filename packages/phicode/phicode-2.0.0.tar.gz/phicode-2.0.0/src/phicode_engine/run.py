import sys
import os
import traceback
import argparse
from .core.phicode_importer import PhicodeFinder

def install(base_path):
    finder = PhicodeFinder(base_path)
    sys.meta_path.insert(0, finder)
    return finder

def main():
    parser = argparse.ArgumentParser(description="PHICODE Runtime Engine")
    parser.add_argument("module_or_file", nargs="?", default="main",
                        help="Module name or .φ file to run")
    parser.add_argument("--version", action="store_true", help="Show version")

    args = parser.parse_args()

    if args.version:
        print("phicode version 2.0.0")
        sys.exit(0)

    target = args.module_or_file.strip()

    if os.path.isfile(target):
        if not target.endswith('.φ'):
            print(f"Error: File must have .φ extension: {target}", file=sys.stderr)
            sys.exit(1)
        src_folder = os.path.dirname(os.path.abspath(target))
        module_name = os.path.splitext(os.path.basename(target))[0]
    else:
        src_folder = os.getcwd()
        module_name = target

    if not os.path.isdir(src_folder):
        print(f"Error: Directory not found: {src_folder}", file=sys.stderr)
        sys.exit(1)

    install(src_folder)

    try:
        __import__(module_name)
    except Exception as e:
        print(f"Error running '{module_name}': {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
