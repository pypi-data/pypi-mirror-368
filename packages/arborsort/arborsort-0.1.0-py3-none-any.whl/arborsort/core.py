from pathlib import Path
from functools import partial
import os
import logging

logger = logging.getLogger(__name__)

class FileOrganizer():
    """
    Organizes files in a given directory by classifying them into folders based on their file types.

    Attributes:
        directory (str or Path): The path to the directory to organize.
    """

    def __init__(self, directory):
        """
        Initializes the FileOrganizer with the target directory.

        Args:
            directory (str or Path): Directory path to organize.

        Raises:
            TypeError: If the provided path is not a folder.
        """
        self.directory = directory
        if not self.is_folder(directory):
            raise TypeError("Please provide a folder!")

    def is_folder(self, directory):
        """
        Checks if the given path is a directory.

        Args:
            directory (str or Path): Path to check.

        Returns:
            bool: True if path is a directory, False otherwise.
        """
        direct = Path(directory)
        return direct.is_dir()

    def verify_folders(self, folder_type, is_empty, item, directory):
        """
        Creates category folders if they do not exist.

        Args:
            folder_type (str): Name of the folder type to verify/create.
            is_empty (bool): Whether the base directory is empty.
            item (Path or None): Current directory item being checked.
            directory (Path): Base directory path.
        """
        if is_empty:
            (directory / folder_type).mkdir(exist_ok=True)
        else:
            if item.stem != folder_type:
                (directory / folder_type).mkdir(exist_ok=True)

    def has_subdirectories(self, path):
        """
        Checks if a directory has any subdirectories.

        Args:
            path (str or Path): Directory path to check.

        Returns:
            bool: True if there is at least one subdirectory, False otherwise.
        """
        return any(os.path.isdir(os.path.join(path, item)) for item in os.listdir(path))

    def return_file_type(self, file):
        """
        Returns the file extension (without the leading dot).

        Args:
            file (Path): File path.

        Returns:
            str: File extension without the dot.
        """
        return file.suffix[1:]

    def create_category_folder(self):
        """
        Ensures that all category folders exist within the base directory.
        Creates folders if they do not exist.
        """
        try:
            directory = Path(self.directory)
            folders = [
                "Images", "Videos", "Documents", "Spreadsheets",
                "Presentations", "Compressed", "Executable", "Code",
                "Database", "Vector Graphics", "Audios",
                "Fonts", "3D Models", "Disk Images", "Others"
            ]
            if self.has_subdirectories(directory):
                for item in directory.iterdir():
                    if item.is_dir():
                        verify_folder = partial(
                            self.verify_folders,
                            is_empty=False,
                            item=item,
                            directory=directory
                        )
                        list(map(verify_folder, folders))
            else:
                verify_folder = partial(
                    self.verify_folders,
                    is_empty=True,
                    item=None,
                    directory=directory
                )
                list(map(verify_folder, folders))
        except OSError as e:
            logger.error(f"Error processing {self.directory} : {e}")

    def move_file(self, file, destination):
        """
        Moves a file to the specified destination folder.

        Args:
            file (Path): File to move.
            destination (Path): Destination folder path.
        """
        try:
            file.rename(destination / file.name)
            logger.info(f"Moved file {file.name} to {destination}")
        except Exception as e:
            logger.error(f"Failed to move file {file.name} to {destination}: {e}")

    def match_file(self, file, directory):
        """
        Matches a file's extension to its category folder and moves it accordingly.

        Args:
            file (Path): File path.
            directory (Path): Base directory where folders exist.
        """
        file_type = self.return_file_type(file)
        logger.debug(f"Matching file {file.name} of type {file_type} in directory {directory}")

        match file_type:
            case 'png' | 'jpg' | 'jpeg' | 'gif' | 'bmp' | 'tiff' | 'tif' | 'svg' | 'webp':
                destination = directory / "Images"
            case 'mp4' | 'avi' | 'mkv' | 'mov' | 'wmv' | 'flv' | 'mpeg' | 'mpg':
                destination = directory / "Videos"
            case 'mp3' | 'wav' | 'aac' | 'ogg' | 'flac' | 'm4a':
                destination = directory / "Audios"
            case 'doc' | 'docx' | 'pdf' | 'txt' | 'rtf' | 'odt':
                destination = directory / "Documents"
            case 'xls' | 'xlsx' | 'csv' | 'ods':
                destination = directory / "Spreadsheets"
            case 'ppt' | 'pptx' | 'odp':
                destination = directory / "Presentations"
            case 'zip' | 'rar' | '7z' | 'tar' | 'gz':
                destination = directory / "Compressed"
            case 'exe' | 'app' | 'apk' | 'bat' | 'sh':
                destination = directory / "Executable"
            case 'py' | 'java' | 'cpp' | 'c' | 'html' | 'css' | 'js' | 'php':
                destination = directory / "Code"
            case 'sql' | 'db' | 'sqlite' | 'mdb':
                destination = directory / "Database"
            case 'ai' | 'psd' | 'eps' | 'indd':
                destination = directory / "Vector Graphics"
            case 'ttf' | 'otf':
                destination = directory / "Fonts"
            case 'obj' | 'fbx' | 'stl' | '3ds':
                destination = directory / "3D Models"
            case 'iso' | 'dmg':
                destination = directory / "Disk Images"
            case _:
                destination = directory / "Others"

        self.move_file(file, destination)

    def place_file_in_folder(self):
        """
        Organizes all files in the directory by classifying and moving them to their respective folders.
        """
        self.create_category_folder()
        try:
            directory = Path(self.directory)
            for item in directory.iterdir():
                if item.is_file():
                    self.match_file(item, directory)
        except OSError as e:
            logger.error(f"Error processing {directory}: {e}")


def organize_files_into_folders(folder):
    """
    Convenience function to organize files in the specified folder.

    Args:
        folder (str or Path): Directory to organize.
    """
    organizer = FileOrganizer(folder)
    organizer.place_file_in_folder()

organizer = FileOrganizer(r"C:\Users\USER\Desktop\Test")
organizer.place_file_in_folder()