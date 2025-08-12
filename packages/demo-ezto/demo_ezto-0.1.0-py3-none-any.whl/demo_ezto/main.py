import sys
import argparse

from .create_project import create_fastapi_project

def main():
    parser = argparse.ArgumentParser(description="Set up a FastAPI Python project.")
    subparsers = parser.add_subparsers(dest="command")
    create_parser = subparsers.add_parser("create", help="Create the project structure")
    args = parser.parse_args()

    if args.command == "create":
        create_fastapi_project()
    else:
        parser.print_help()
        sys.exit(1)