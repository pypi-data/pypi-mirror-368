import os
import shutil
import requests
import zipfile

def download_file(url: str, save_to: str):
    """
    Downloads a file from the specified URL and saves it to the given path.

    Args:
        url (str): The URL of the file to be downloaded.
        save_to (str): The local file path where the downloaded file will be saved.
    """

    response = requests.get(url)
    with open(save_to, 'wb') as f:
        f.write(response.content)

def extract_zip_file(zip_file: str, extract_to: str):
    """
    Extracts the contents of a ZIP file to a specified directory.

    Args:
        zip_file (str): The path to the ZIP file to be extracted.
        extract_to (str): The directory where the contents will be extracted. 
                          If the directory does not exist, it will be created.
    """

    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        os.makedirs(extract_to, exist_ok=True)
        zip_ref.extractall(extract_to)

def get_file_list(directory):
    """
    Walks the given directory and returns a list of files.

    Args:
        directory (str): The directory to walk.

    Returns:
        list: A list of file paths.
    """
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            files.append(os.path.join(root, file))
    return file_list

def get_dir_list(directory, relative=False):
    """
    Generates a list of directories within the specified directory.

    Args:
        directory (str): The directory to walk.
        relative (bool, optional): If True, returns directory paths relative to the input directory. Defaults to False.

    Returns:
        list: A list of directory paths.
    """

    dir_list = []
    for root, dirs, _ in os.walk(directory):
        for dir in dirs:
            if relative:
                relative_root = root.replace(directory, '')
                dir_list.append(os.path.join(relative_root, dir))
            else:
                dir_list.append(os.path.join(root, dir))
    return dir_list


def get_files_by_extension(directory, extensions, relative=False):
    """
    Retrieves a list of files with specified extensions from a directory.

    Args:
        directory (str): The directory to search for files.
        extensions (list): A list of file extensions to filter by.
        relative (bool, optional): If True, returns file paths relative to the input directory. Defaults to False.

    Returns:
        list: A list of file paths with the specified extensions.
    """

    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_ext = os.path.splitext(file)[1].lower()

            for ext in extensions:
                if ext.casefold() == file_ext.casefold():
                    if relative:
                        relative_root = root.replace(os.path.join(directory, ''), '')
                        file_list.append(os.path.join(relative_root, file))
                    else:
                        file_list.append(os.path.join(root, file))

    return file_list

def get_files_containing_string(directory, string, relative=False):
    """
    Retrieves a list of files in a directory and its subdirectories that contain a specified string.

    Args:
        directory (str): The directory to search for files.
        string (str): The string to search for in the files.
        relative (bool, optional): If True, returns file paths relative to the input directory. Defaults to False.

    Returns:
        list: A list of file paths that contain the specified string.
    """
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            if string.casefold() in file.casefold():
                if relative:
                    relative_root = root.replace(directory, '')
                    file_list.append(os.path.join(relative_root, file))
                else:
                    file_list.append(os.path.join(root, file))

    return file_list


def get_dirs_containing_string(directory, string, relative=False):
    """
    Retrieves a list of directories in a specified directory and its subdirectories that contain a specified string.

    Args:
        directory (str): The directory to search for directories.
        string (str): The string to search for in the directory names.
        relative (bool, optional): If True, returns directory paths relative to the input directory. Defaults to False.

    Returns:
        list: A list of directory paths that contain the specified string.
    """

    dir_list = []
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            if string.casefold() in dir.casefold():
                if relative:
                    relative_root = root.replace(directory, '')
                    dir_list.append(os.path.join(relative_root, dir))
                else:
                    dir_list.append(os.path.join(root, dir))

    return dir_list

def directory_contains_directory(directory, subdirectory):
    """
    Checks if a directory contains a specified subdirectory.

    Args:
        directory (str): The directory to search in.
        subdirectory (str): The subdirectory to search for.

    Returns:
        bool: True if the subdirectory is found, False otherwise.
    """
    for _, dirs, _ in os.walk(directory):
        for dir in dirs:
            if subdirectory.casefold() in dir.casefold():
                return True
    return False

def directory_contains_file(directory, filename):
    """
    Checks if a directory contains a specified file.

    Args:
        directory (str): The directory to search in.
        filename (str): The file to search for.

    Returns:
        bool: True if the file is found, False otherwise.
    """
    for _, _, files in os.walk(directory):
        for file in files:
            if filename.casefold() in file.casefold():
                return True
    return False

def directory_contains_file_with_extension(directory, extension):
    """
    Checks if a directory contains at least one file with a specified file extension.

    Args:
        directory (str): The directory to search in.
        extension (str): The file extension to search for, including the leading period (e.g. '.txt').

    Returns:
        bool: True if a file with the specified extension is found, False otherwise.
    """
    for _, _, files in os.walk(directory):
        for file in files:
            if extension.casefold() in os.path.splitext(file)[1].casefold():
                return True
    return False

def create_directory(directory_path):
    """
    Creates a directory at the specified path.

    Args:
        directory_path (str): The path where the directory should be created.

    Notes:
        If the directory already exists, this function does nothing.
    """

    os.makedirs(directory_path, exist_ok=True)

def create_subdirectory(parent_dir, subdirectory_name):
    """
    Creates a subdirectory inside the given parent directory.

    Args:
        parent_dir (str): The path of the parent directory.
        subdirectory_name (str): The name of the subdirectory to create.

    Notes:
        If the subdirectory already exists, this function does nothing.
    """
    subdirectory_path = os.path.join(parent_dir, subdirectory_name)
    os.makedirs(subdirectory_path, exist_ok=True)

def copy_file(src_file_path, dest_file_path):
    """
    Copies a file from the source path to the destination path.

    Args:
        src_file_path (str): The path to the source file.
        dest_file_path (str): The path where the file should be copied to.

    Notes:
        This function preserves the file's metadata, such as modification and access times.
    """

    shutil.copy2(src_file_path, dest_file_path)

def copy_files(src_paths, dest_dir, enumerate_dups=True):
    """
    Copies files from the source paths to the destination directory.

    Args:
        src_paths (list): A list of paths to the source files.
        dest_dir (str): The path to the destination directory.
        enumerate_dups (bool, optional): If True, appends a number to the file name if a file with the same name already exists in the destination directory. Defaults to True.

    Notes:
        This function preserves the file's metadata, such as modification and access times.
    """

    for src_path in src_paths:
        filename = os.path.basename(src_path)
        dest_path = os.path.join(dest_dir, filename)

        if enumerate_dups:
            counter = 1
            while os.path.exists(dest_path):
                filename, extension = os.path.splitext(filename)
                filename = f"{filename}_{counter}{extension}"
                dest_path = os.path.join(dest_dir, filename)
                counter += 1

        shutil.copy2(src_path, dest_path)


def move_file(src_file_path, dest_file_path):
    """
    Moves a file from the source path to the destination path.

    Args:
        src_file_path (str): The path to the source file.
        dest_file_path (str): The path where the file should be moved to.

    Notes:
        This function preserves the file's metadata, such as modification and access times.
    """
    
    shutil.move(src_file_path, dest_file_path)

def directory_exists(directory_path):
    """
    Checks if a directory exists at the specified path.

    Args:
        directory_path (str): The path to check.

    Returns:
        bool: True if the directory exists, False otherwise.
    """
    return os.path.exists(directory_path) and os.path.isdir(directory_path)

def file_exists(file_path):
    """
    Checks if a file exists at the specified path.

    Args:
        file_path (str): The path to check.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    return os.path.exists(file_path) and os.path.isfile(file_path)

def delete_directory(directory_path):
    """
    Deletes the specified directory and all its contents.

    Args:
        directory_path (str): The path to the directory to delete.

    Notes:
        This function does not raise an error if the directory does not exist.
    """
    if os.path.exists(directory_path):
        if os.path.isdir(directory_path):
            shutil.rmtree(directory_path)

def delete_file(file_path):
    """
    Deletes the specified file.

    Args:
        file_path (str): The path to the file to be deleted.

    Notes:
        This function does not raise an error if the file does not exist.
    """

    if os.path.exists(file_path):
        os.remove(file_path)

def get_file_extension(file_path):
    """
    Retrieves the file extension from the given file path.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The file extension, in lowercase.
    """
    return os.path.splitext(file_path)[1].lower()

def get_file_name(file_path):
    """
    Retrieves the file name from the given file path.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The file name.
    """
    return os.path.basename(file_path)

def get_file_directory(file_path):
    """
    Retrieves the directory path from the given file path.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The directory path containing the file.
    """

    return os.path.dirname(file_path)

def recreate_directory(directory_path):
    """
    Deletes and then creates a directory at the specified path.

    Args:
        directory_path (str): The path to the directory to be recreated.

    Notes:
        If the directory does not exist, it will be created.
    """

    delete_directory(directory_path)
    create_directory(directory_path)

def copy_directory(src_dir, dest_dir):
    """
    Copies a directory from the source directory to the destination directory.

    Args:
        src_dir (str): The path to the source directory.
        dest_dir (str): The path to the destination directory.

    Notes:
        If the destination directory does not exist, it will be created. If it does exist, its contents will be overwritten.
    """
    
    shutil.copytree(src_dir, dest_dir)