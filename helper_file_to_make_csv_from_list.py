import csv
import os
from typing import List

def make_csv(data_list: List[str], output_file: str, header: str = 'Conversation ID') -> None:
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([header])
        for item in data_list:
            writer.writerow([item])