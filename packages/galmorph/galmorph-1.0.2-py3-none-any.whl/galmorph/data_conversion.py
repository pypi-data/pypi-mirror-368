import pandas as pd
import numpy as np
import h5py
from typing import Dict
from tqdm import tqdm  # Optional: Uncomment for progress tracking

def print_attrs(name: str, obj: h5py.Group) -> None:
    """Prints the attributes of HDF5 objects."""
    print(name)
    for key, val in obj.attrs.items():
        print(f"    {key}: {val}")


def convert_to_dataframe(snapshot: str, group: h5py.Group) -> pd.DataFrame:
    """Converts a snapshot group into a pandas DataFrame with snapshot number."""
    snapshot_num = snapshot.split("_")[1]  # Robust extraction
    # print(snapshot.split("_"))
    n_rows = next(iter(group.values())).shape[0]

    data_dict: Dict[str, np.ndarray] = {
        "Snapshot": np.full(n_rows, snapshot_num, dtype="int16")
    }
    for col in group:
        data_dict[col] = group[col][:]

    return pd.DataFrame(data_dict)


def main(filepath: str) -> pd.DataFrame:
    """Reads HDF5 data and converts all snapshots into a single DataFrame."""
    with h5py.File(filepath, 'r') as f:
        # f.visititems(print_attrs)  # Uncomment to inspect file structure
        snapshot_keys = [k for k in f.keys() if k.startswith("Snapshot_")]
        if not snapshot_keys:
            raise ValueError("No snapshot groups found in the file.")

        all_dataframes = []
        # for key in tqdm(snapshot_keys, colour='GREEN'):  # Optional: tqdm for progress
        for key in snapshot_keys:
            group = f[key]
            df = convert_to_dataframe(key, group)
            all_dataframes.append(df)

    return pd.concat(all_dataframes, ignore_index=True)

if __name__ == "__main__":
    filepath = "morphologies_deeplearn.hdf5"
    df_all = main(filepath)
    print(df_all.head(), df_all.shape)
    # Save the final DataFrame to a pickle file
    # df_all.to_pickle("morphologies_snapshot_data.pkl")

    # df_all.to_csv("galaxies_morph.csv", index=False)
