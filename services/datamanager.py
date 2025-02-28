import os
import pandas as pd

def get_inbound_file_list():
    directory = r"C:\Users\JoeDuppstadt\Downloads\inbound"
    return [os.path.join(directory, f) for f in os.listdir(directory) if
                  os.path.isfile(os.path.join(directory, f))]


def get_reference_data(location):
    dataset = pd.read_csv(location)
    abbreviation = dataset['abbreviation'].tolist()
    full_name = dataset['full_name'].tolist()
    return abbreviation, full_name
