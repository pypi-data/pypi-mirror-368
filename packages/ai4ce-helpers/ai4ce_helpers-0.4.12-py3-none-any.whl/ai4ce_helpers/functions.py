# Here is the place to but general helper functions

import ast
import json
from pathlib import Path
import toml
import pandas as pd

from ._backend_calls import _backend_POST, _backend_PUT, _backend_GET


def load_file(filename: Path) -> dict | pd.DataFrame:
    """
    Load data from a file. The function currently supports JSON files.

    Parameters:
    filename (Path): The path to the file.

    Returns:
    dict: The data loaded from the file if it's a JSON.
    """
    if filename.suffix == '.csv':
        df = pd.read_csv(filename, sep=',', header=0,
                         index_col=None, na_values=['NA', '?'])
        return df

    elif filename.suffix == '.json':
        with open(filename, 'r') as file:
            return json.load(file)

    elif filename.suffix == '.toml':
        with open(filename, 'r') as file:
            return toml.load(file)

    else:
        raise ValueError(
            "You need to add the file format to the load_file function.")


