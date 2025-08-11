import io
import tarfile
from pathlib import Path


class Tar:
    """
    Class to handle tar.gz files
    """
    def __init__(self, path: Path):
        self.tar = tarfile.open(path, "r:gz")
        self.name_list = self.tar.getnames()

    def get_file(self, file_name: str) -> io.BufferedReader:
        """
        From file name, get file data
        Args:
            file_name: name of the file
        Returns:
            file: file as reader, should be opened with any dedicated reader

        """
        file = None
        if file_name in self.name_list:
            member = self.tar.getmember(file_name)
            file = self.tar.extractfile(member)
        return file

    def extract_file(self, file_name: str, folder: Path) -> Path:
        """
        From file name extract the file
        Args:
            file_name: name of the file
            folder: folder where to extract the file
        Returns:
            file_path: file path of the extract file

        """
        if not folder.exists():
            folder.mkdir(parents=True)
        file_path = None
        if file_name in self.name_list:
            member = self.tar.getmember(file_name)
            self.tar.extract(member, folder)
            file_path = folder / file_name
        return file_path

    def extract(self, folder: Path):
        """
        Extract all files at once in given folder
        Args:
            folder: folder where to extract the files
        """
        if not folder.exists():
            folder.mkdir(parents=True)
        self.tar.extractall(folder)

    def __del__(self):
        self.tar.close()


def create_tar_from_folder(tar_path: Path, folder_path: Path):
    """
    Create tar from one folder, take all files within this folder and add to tar.gz file
    Args:
        tar_path: output tar.gz file
        folder_path: input folder path
    """
    with tarfile.open(tar_path, "w:gz") as tar:
        for file in folder_path.iterdir():
            tar.add(file, arcname=file.name)
