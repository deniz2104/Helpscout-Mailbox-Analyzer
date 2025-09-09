from typing import List, Tuple
import csv
from helper_file_to_make_csv_from_list import make_csv

class FilterWporgConversations():
    def __init__(self):
        self.ids_file = 'CSVs/filtered_free_conversations_ids.csv'
        self.tags_file = 'CSVs/filtered_free_conversations_tags.csv'
        self.target_tag = 'team reply'
        self.output_file = 'CSVs/filtered_wporg_conversations.csv'

    def _read_csv(self, file_path: str, is_tags: bool = False) -> List[str]:
        data_list = []
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)  # Skip header
                for row in reader:
                    if is_tags:
                        data_list.append(','.join(row).lower())
                    else:
                        data_list.append(row[0])
        except FileNotFoundError:
            print(f"Error: {file_path} not found")
        return data_list

    def _get_conversation_data(self) -> Tuple[List[str], List[str]]:
        conversation_ids = self._read_csv(self.ids_file)
        tags_list = self._read_csv(self.tags_file, is_tags=True)

        min_length = min(len(conversation_ids), len(tags_list))
        if len(conversation_ids) != len(tags_list):
            print(f"Warning: Mismatch in row counts. Using shortest length: {min_length}")
        
        return conversation_ids[:min_length], tags_list[:min_length]

    def _filter_by_tag(self, conversation_ids: List[str], tags_list: List[str]) -> Tuple[List[str], int]:
        filtered_data = [(conv_id, tags) for conv_id, tags in zip(conversation_ids, tags_list) if self.target_tag in tags]
        filtered_ids = [item[0] for item in filtered_data]
        return filtered_ids, len(filtered_ids)

    def process_and_export(self) -> None:
        conversation_ids, tags_list = self._get_conversation_data()
        
        if not conversation_ids or not tags_list:
            print("Could not load necessary data. Exiting.")
            return

        filtered_ids, team_reply_count = self._filter_by_tag(conversation_ids, tags_list)

        if filtered_ids:
            make_csv(filtered_ids, self.output_file)
            print(f"Exported {len(filtered_ids)} conversations with '{self.target_tag}' to {self.output_file}")
            print(f"Total '{self.target_tag}' occurrences: {team_reply_count}")
        else:
            print(f"No conversations found with the tag '{self.target_tag}'. No file exported.")

def main():
    filter_wporg = FilterWporgConversations()
    filter_wporg.process_and_export()

if __name__ == "__main__":
    main()