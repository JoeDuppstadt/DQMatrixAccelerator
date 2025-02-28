import os

def get_inbound_file_list():
    directory = r"C:\Users\JoeDuppstadt\Downloads\inbound"
    return [os.path.join(directory, f) for f in os.listdir(directory) if
                  os.path.isfile(os.path.join(directory, f))]

