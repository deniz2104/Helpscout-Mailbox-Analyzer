from typing import List, Tuple
import csv
import os
from helper_file_to_make_csv_from_list import make_csv

## !IMPORTANT!

class FilterWporgConversations():
    def __init__(self):
        self.ids_file = 'CSVs/filtered_free_conversations_ids.csv'
        self.tags_file = 'CSVs/filtered_free_conversations_tags.csv'
        self.target_tag = 'team reply'

    def make_list_from_csv(self, file_path: str, is_tags: bool = False) -> List[str]:
        data_list = []
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) 
            for row in reader:
                if row:
                    if is_tags:
                        data_list.append(','.join(row))
                    else:
                        data_list.append(row[0])
                elif is_tags:
                    data_list.append('')
        return data_list

    def validate_csv_files(self) -> bool:
        if not os.path.exists(self.ids_file):
            print(f"Error: {self.ids_file} not found")
            return False

        if not os.path.exists(self.tags_file):
            print(f"Error: {self.tags_file} not found")
            return False
            
        return True

    def load_conversations_and_tags(self) -> Tuple[List[str], List[str]]:
        if not self.validate_csv_files():
            return [], []

        conversation_ids = self.make_list_from_csv(self.ids_file)
        tags_list = self.make_list_from_csv(self.tags_file, is_tags=True)

        if len(conversation_ids) != len(tags_list):
            print(f"Warning: Mismatch in row counts - IDs: {len(conversation_ids)}, Tags: {len(tags_list)}")
            min_length = min(len(conversation_ids), len(tags_list))
            conversation_ids = conversation_ids[:min_length]
            tags_list = tags_list[:min_length]

        return conversation_ids, tags_list

    def filter_conversations(self) -> Tuple[List[str], int]:
        conversation_ids, tags_list = self.load_conversations_and_tags()

        filtered_ids = []
        team_reply_count = 0
        for conv_id, tags in zip(conversation_ids, tags_list):
            if self.target_tag in tags.lower():
                filtered_ids.append(conv_id)
                team_reply_count += 1

        return filtered_ids, team_reply_count

    def export_filtered_conversations(self, output_file: str) -> None:
        filtered_ids, _ = self.filter_conversations()
        make_csv(filtered_ids, output_file)

def main():
    filter_wporg = FilterWporgConversations()
    filter_wporg.export_filtered_conversations('CSVs/filtered_wporg_conversations.csv')

if __name__ == "__main__":
    main()
