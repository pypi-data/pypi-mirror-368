from pathlib import Path
import shutil

from lacbox.htc.htc_file import HTCFile


def _clean_directory(htc_dir, clean_htc):
    """Clean or create a directory as requested"""
    # sanitize inputs
    htc_dir = Path(htc_dir)
    # if the folder exists but we want a clean run
    if htc_dir.is_dir() and clean_htc:
        print(f'! Folder {htc_dir} exists: deleting contents. !')
        shutil.rmtree(htc_dir) # delete the folder
        htc_dir.mkdir(parents=True)  # make an empty folder
    # if the folder doesn't exists
    elif not htc_dir.is_dir():
        htc_dir.mkdir(parents=True)  # make the folder
    return
