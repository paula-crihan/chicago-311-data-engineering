import os
import pandas as pd

from src.config import RAW_DATA_PATH


def save_to_parquet(data, filename):
    os.makedirs(RAW_DATA_PATH, exist_ok=True)

    dataframe = pd.DataFrame(data)

    file_path = os.path.join(
        RAW_DATA_PATH,
        filename
    )

    dataframe.to_parquet(
        file_path,
        engine="pyarrow",
        index=False
    )

    print(f"Saved {len(dataframe)} records to {file_path}")

    return file_path