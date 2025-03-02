import os
import pandas as pd
from openpyxl.reader.excel import load_workbook

directory = r"C:\Users\JoeDuppstadt\Downloads\inbound"

def get_inbound_file_list():
    return [os.path.join(directory, f) for f in os.listdir(directory) if
                  os.path.isfile(os.path.join(directory, f))], os.listdir(directory)

def remove_old_dq_matrix():
    try:
        os.remove(r"C:\Users\JoeDuppstadt\Downloads\inbound\DQMatrixOut.xlsx")
    except Exception as e:
        Exception('Close old DQ Matrix Excel')

def get_reference_data(location):
    dataset = pd.read_csv(location)
    abbreviation = dataset['abbreviation'].tolist()
    full_name = dataset['full_name'].tolist()
    return abbreviation, full_name

def write_to_excel(data, output_file, sheet_name):
    file_location = os.path.join(directory, output_file)
    print(file_location)
    #append sheet to existing file
    if os.path.exists(file_location):
        # Load the existing workbook and append new sheet
        with pd.ExcelWriter(file_location, engine='openpyxl', mode='a', if_sheet_exists='new') as writer:
            # Write or preserve existing sheets
            data.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        # Create new file
        with pd.ExcelWriter(file_location, engine='openpyxl') as writer:
            data.to_excel(writer, sheet_name=sheet_name, index=False)

def load_excel(file):
    return load_workbook(os.path.join(directory, file))

def save_excel_formating(workbook, file):
    workbook.save(os.path.join(directory, file))