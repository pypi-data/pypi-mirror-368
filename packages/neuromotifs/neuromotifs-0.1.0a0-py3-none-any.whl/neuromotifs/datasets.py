import pandas as pd
from pathlib import Path
from importlib import resources


def load_motifs(path: str | Path = None) -> pd.DataFrame:
    """
    Load motifs CSV.
    If no path is given, loads neuromotifs/data/nmc/motifs.csv from the package.
    """
    if path is None:
        with resources.path("neuromotifs.data.nmc", "motifs.csv") as p:
            path = p
    print(f"Loading {path}..")
    return pd.read_csv(path)
