import csv
import os

def export_csv_to_list(file_path: str) -> list:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    data_list = []
    with open(file_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if row:
                data_list.append(row[0])
    return data_list