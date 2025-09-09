import csv
from typing import List
def make_csv(data_list: List[str], output_file: str, header: str = 'Conversation ID') -> None:
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([header])
        for item in data_list:
            writer.writerow([item])