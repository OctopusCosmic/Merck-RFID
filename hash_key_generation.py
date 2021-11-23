import pandas as pd
def generate_hash_key(row, features_selected):
    hash_key = ""
    for feature in features_selected:
        hash_key += row[feature] + " "

    return
def append_hash_key(data: pd.DataFrame, features_selected: list):
    # generate hash_key by information from rows
    data["hash_key"] = data.apply(generate_hash_key, axis=1)

