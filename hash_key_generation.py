import pandas as pd
import hashlib
pd.set_option('display.max_columns', None)
def generate_hash_key(row, features_selected):
    # initialize hash_key as empty string
    hash_key = ""
    # concatenate values from given features to generate hash_key
    for feature in features_selected:
        hash_key += str(row[feature]) + ""
    hash_key = hashlib.sha256(hash_key.encode()).hexdigest()
    # return hash_key
    return hash_key

def check_hash(hash_key, features_selected):
    check = (hash_key == hashlib.sha256(hash_key.encode()).hexdigest())
    return check

def append_hash_key(data: pd.DataFrame, features_selected: list):
    # generate hash_key by information from rows

    # apply generate_hash_key function to selected columns
    #   and assign the resulting value to a new column called hash_key
    data["hash_key"] = data.apply(lambda row: generate_hash_key(row, features_selected), axis=1)
    # return resulting data with one more column
    return data

def main():
    # read csv from file, this part will be substituted by pulling data from database
    data = pd.read_csv("dummy_data.csv", index_col=False)
    # print original data from csv
    print(data)
    # define selected feature, this part will be substituted by selected feature from front end
    features_selected = ["batch_no","MK_number","sample_number"]
    # apply append_hash_key function to add new column called hash_key
    data = append_hash_key(data, features_selected)
    # nothing but for separating
    print("="*70)
    # print the new data having hash_key column
    print(data)

main()
