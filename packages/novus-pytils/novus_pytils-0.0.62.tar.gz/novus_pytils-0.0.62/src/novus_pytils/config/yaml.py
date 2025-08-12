import yaml
from novus_pytils.files import file_exists, get_files_by_extension

def load_yaml(filepath : str) -> dict:
    """
    Load a yaml file and return the contents as a dictionary.

    Args:
        filepath (str): The path to the yaml file.

    Returns:
        dict: The contents of the yaml file as a dictionary.
    """

    if not file_exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)
    
def get_yaml_files(dir_path : str) -> list:
    """
    Get all yaml files in a directory.

    Args:
        dir_path (str): The path to the directory.

    Returns:
        list: A list of paths to yaml files in the directory.
    """
    return get_files_by_extension(dir_path, [".yaml", ".yml"])
    
