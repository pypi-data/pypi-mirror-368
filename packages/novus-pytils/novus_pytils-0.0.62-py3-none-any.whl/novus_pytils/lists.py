def remove_empty_lines_from_list(list):
    """
    Removes empty lines from a list of strings.

    :param list: List of strings.
    :return: List of strings with empty lines removed.
    """
    return [x for x in list if x]

def print_list(list):
    """
    Prints a list of items.

    :param list: List of items to print.
    """
    for item in list:
        print(item)

def write_list_to_file(file_name, lines):
    """
    Writes lines to a file, adding a newline to the end of each line.

    :param str file_name: Name of the file to write.
    :param List[str] lines: List of strings to write to the file.
    """
    
    with open(file_name, 'w') as file:
        for line in lines:
            file.write(line + '\n')

def read_list_from_file(file_name):
    """
    Reads lines from a file, stripping whitespace from each.

    :param str file_name: Name of the file to read.
    :return: List of strings, each line from the file with whitespace stripped.
    :rtype: List[str]
    """
    
    with open(file_name, 'r') as file:
        lines = file.readlines()
    return [line.strip() for line in lines]
