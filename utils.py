import hashlib
import os
import shutil



def unzip_folder(file_name)->str:
    received_folder = file_name[:-4]
    shutil.unpack_archive(file_name, received_folder)
    os.remove(file_name)
    return received_folder

def calculate_hash(file_path: str) -> str:
    """Calculates SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def zip_folder(path) -> str:
        shutil.make_archive(path, 'zip', path)
        file_path = f"{path}.zip"
        return file_path