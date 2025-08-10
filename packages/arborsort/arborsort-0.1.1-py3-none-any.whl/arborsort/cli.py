import argparse
import logging
from arborsort.core import organize_files_into_folders
from pathlib import Path


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)

def main():
    parser = argparse.ArgumentParser(description="Classify Files into Folders base on their Type")
    parser.add_argument("command", choices=["classify"], help="Command to run")
    parser.add_argument("folder", type=str, help="Path to the folder")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug output")
    args = parser.parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    folder_path = Path(args.folder).resolve()
    if args.command == "classify":
        logger.info(f"Moving files from {folder_path} into Folders based on their type.") 
        organize_files_into_folders(folder_path)
        logger.info("Done ✅")   

if __name__ == "__name__":
    main()        