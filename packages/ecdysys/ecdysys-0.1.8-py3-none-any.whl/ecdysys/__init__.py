import argparse, importlib.metadata
from .utils.main import check_update, prepare_pkgms, update

def main() -> None:

    pkg_managers, err_msg = prepare_pkgms()

    parser = argparse.ArgumentParser(description="Python CLI to update your system packages")
    parser.add_argument("-v", "--version", action="store_true", help="Print version")
    parser.add_argument("-l", "--list", action="store_true" ,help="List available updates")
    parser.add_argument("-u", "--update", action="store_true", help="Update package")
    parser.add_argument("--no-spinner", action="store_true", help="Doesn't show spinner when listing updates")
    args = parser.parse_args()

    if args.list:
        print(check_update(pkg_managers, err_msg, args.no_spinner))
    elif args.update:
        update(pkg_managers, err_msg)
    elif args.version:
        print(f"Ecdysys v{importlib.metadata.version("ecdysys")}")
