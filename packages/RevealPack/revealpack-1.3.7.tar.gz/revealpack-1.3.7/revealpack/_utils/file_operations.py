import os
import shutil
import filecmp
import logging
import fnmatch
import csv
from pathlib import Path

ignore = ["*.DS_Store", "*.ffs_db", "__pycache__"]


def copy_and_overwrite(src, dest, copied_files=None):
    """Copy directory from src to dest, overwrite if different. Optionally return a list of copied file paths."""
    if copied_files is None:
        copied_files = []
    if isinstance(src, Path):
        src = str(src)
    src = src.replace('\\', '/')
    
    if not os.path.exists(dest):
        shutil.copytree(src, dest)
        logging.info(f"Copying directory {dest}.")
        for root, _, files in os.walk(dest):
            for file in files:
                copied_files.append(os.path.join(root, file))
        return copied_files

    for item in os.listdir(src):
        src_item = os.path.join(src, item)
        dest_item = os.path.join(dest, item)

        if os.path.isdir(src_item):
            copy_and_overwrite(src_item, dest_item, copied_files)
        else:
            copy_file_if_different(src_item, dest_item, copied_files)

    return copied_files


def copy_file_if_different(src, dest, copied_files=[]):
    """
    Copy a file from src to dest, overwrite if different.

    Parameters:
    - src (str): Source file path
    - dest (str): Destination file path
    """
    # Convert src to string path if it's a Path object and normalize path separators
    if isinstance(src, Path):
        src = str(src)
    src = src.replace('\\', '/')
    # Create parent directory if it doesn't exist
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    # Check if src file matches any pattern in the ignore list
    src_file_name = os.path.basename(src)
    if any(fnmatch.fnmatch(src_file_name, pattern) for pattern in ignore):
        logging.info(f"Skipping file {src} as it matches ignore pattern.")
        return

    if os.path.exists(dest):
        if not filecmp.cmp(src, dest, shallow=False):
            shutil.copy2(src, dest)
            logging.info(f"Overwriting file {dest} because it's different.")
        # else:
        # logging.info(f"File {dest} is identical, skipping copy.")
    else:
        shutil.copy2(src, dest)
        logging.info(f"Copying file {dest}.")
    copied_files.append(dest)

def get_theme_path(config) -> str:
    """Locate theme specified in config.json."""
    theme_name = config["theme"]
    theme_path = Path(theme_name)
    
    source_root = Path(config["directories"]["source"]["root"])
    theme_dir_in_reveal = source_root / "cached" / "reveal.js" / "css" / "theme" / "source"
    custom_theme_dir = Path("custom_theme")
    # Check if the theme is a builtin theme in the reveal.js directory
    def is_builtin_theme(theme_name):
        for filename in theme_dir_in_reveal.iterdir():
            if filename.stem == theme_name:
                return filename
        return None
    # Determine the theme path
    if theme_path.suffix == '.css':
        theme_full_path = theme_path
    elif theme_path.suffix in {'.scss', '.sass'}:
        if theme_path.is_file():
            theme_full_path = theme_path
        elif (custom_theme_dir / theme_path).is_file():
            theme_full_path = custom_theme_dir / theme_path
        elif is_builtin_theme(theme_path.stem):
            theme_full_path = is_builtin_theme(theme_path.stem)
        else:
            theme_full_path = None
    else:
        # No extension provided, assume .scss
        if (theme_path.with_suffix('.scss')).is_file():
            theme_full_path = theme_path.with_suffix('.scss')
        elif (custom_theme_dir / theme_path.with_suffix('.scss')).is_file():
            theme_full_path = custom_theme_dir / theme_path.with_suffix('.scss')
        elif is_builtin_theme(theme_path.stem):
            theme_full_path = is_builtin_theme(theme_path.stem)
        else:
            theme_full_path = custom_theme_dir / theme_path.with_suffix('.scss').name
    if theme_full_path is None or not theme_full_path.exists():
        return ""
    else:
        return str(theme_full_path)

def cleanup_temp_files(files_list):
    """Delete specified files and remove their parent directories if they become empty."""
    for file_path in files_list:
        # Delete the file if it exists
        if os.path.isfile(file_path):
            os.remove(file_path)
            logging.debug(f"Deleted file: {file_path}")
        else:
            logging.warning(f"File not found: {file_path}")
        
        # Check if the parent directory exists and is empty, then remove it
        parent_dir = os.path.dirname(file_path)
        while parent_dir:
            if os.path.exists(parent_dir):
                if not os.listdir(parent_dir):  # Check if directory is empty
                    os.rmdir(parent_dir)
                    logging.debug(f"Deleted empty directory: {parent_dir}")
                else:
                    break  # Stop if directory is not empty
            else:
                logging.debug(f"Directory does not exist: {parent_dir}")
                break  # Exit the loop if the directory doesn't exist
            
            parent_dir = os.path.dirname(parent_dir)

def get_delimiter_from_file(file_path: str) -> str:
    # First check file extension
    file_extension = Path(file_path).suffix.lower()
    if file_extension == '.csv':
        return ','
    elif file_extension == '.tsv':
        return '\t'
    
    try:
        with open(file_path, 'r') as csvfile:
            # If not csv/tsv, try to detect delimiter
            content = csvfile.read()
            delimiter = str(csv.Sniffer().sniff(content).delimiter)
            return delimiter
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        raise
    except csv.Error as e:
        logging.error(f"Error detecting delimiter in file '{file_path}': {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error while processing file '{file_path}': {e}")
        raise

def parse_delimited_file(file_path: str) -> list:
    """Reads a file and returns a list of values based on the detected delimiter."""
    delimiter = get_delimiter_from_file(file_path)
    value_list = []
    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=delimiter)
            for row in reader:
                # Extend the value_list
                value_list.extend([value.strip() for value in row if value.strip()])
        logging.info(f"Successfully parsed {len(value_list)} element(s) from file '{file_path}'.")
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logging.error(f"Failed to parse file '{file_path}': {e}")
        raise
    return value_list

def clean_build_directory(config):
    build_dir = config['directories']['build']
    if os.path.exists(build_dir):
        for file in os.listdir(build_dir):
            file_path = os.path.join(build_dir, file)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                logging.debug(f"Successfully removed '${file_path}'.")
            except Exception as e:
                logging.error(f'Failed to delete {file_path}. Reason: {e}')