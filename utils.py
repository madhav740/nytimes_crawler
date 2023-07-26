import uuid
import os
import requests
import re
import csv
import constant
from excel_writer import ExcelWriter

def download_image(image_url, download_directory: 'output'):
    file_name = f"{os.path.join(os.getcwd(), download_directory)}/{uuid.uuid4()}.jpg"
    response = requests.get(image_url)
    if response.status_code != 200:
        return "Failed to Download image"
    else:
        with open(file_name, "wb") as f:
            f.write(response.content)
        return file_name

def contains_monetary_values(text):
    pattern = r"\$[\d,.]+|\b\d+(\.\d{1,2})?\s?(billion|million|thousand)?\s?(dollars|USD)?\b"
    return bool(re.search(pattern, text))

def create_csv_file(output_dir: "output", file_name: "nytimes.csv"):
    file_name = f"{os.path.join(os.getcwd(), output_dir)}/{file_name}"
    with open(file_name, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=constant.CSV_FIELD_NAMES)
        writer.writeheader()

def append_rows_in_csv_file(record, output_dir: 'output', file_name: "nytimes.csv"):
    file_name = f"{os.path.join(os.getcwd(), output_dir)}/{file_name}"
    with open(file_name, "a+", newline="") as csvfile:
        csv.DictWriter(csvfile, fieldnames=constant.CSV_FIELD_NAMES).writerow(record)

def create_excel_file(output_dir: 'output', file_name: "nytimes"):
    excel_writer = ExcelWriter()
    excel_file = f"{os.path.join(os.getcwd(), output_dir)}/{file_name}"
    excel_writer.create_excel_file(excel_file)
    excel_writer.rename_sheet(excel_file, 'Sheet', file_name)
    excel_writer.append_row_to_sheet(constant.CSV_FIELD_NAMES, excel_file, file_name)


def append_rows_in_excel_file(record,output_dir: 'output', file_name: "nytimes"):
    excel_writer = ExcelWriter()
    excel_file = f"{os.path.join(os.getcwd(), output_dir)}/{file_name}"
    excel_writer.append_row_to_sheet(record, excel_file, file_name)


