import pandas as pd

def to_frame(input) -> pd.DataFrame:
    """
    Takes a list of lists or a dict and returns a pandas DataFrame object
    """
    
    return pd.DataFrame(input)


def write_csv(df : pd.DataFrame, filepath : str) -> None:
    """
    Writes a pandas DataFrame to a CSV file.

    Parameters
    ----------
    df : pandas DataFrame
        DataFrame to write to CSV
    filepath : str
        Path to write CSV file

    Returns
    -------
    None
    """
    df.to_csv(filepath, index=False)
