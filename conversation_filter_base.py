import csv
import os
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional


class ConversationFilterBase(ABC):
    def __init__(self, ids_file: str, tags_file: str, target_tag: str):
        self.ids_file = ids_file
        self.tags_file = tags_file
        self.target_tag = target_tag

    def export_csv_to_list(self, file_path: Optional[str] = None) -> List[str]:
        if file_path is None:
            file_path = self.ids_file
            
        data_list = []
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if row:
                    data_list.append(row[0])
        return data_list

    def make_list_from_csv(self, file_path: str, is_tags: bool = False) -> List[str]:
        data_list = []
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
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
            # Use the minimum length to avoid index errors
            min_length = min(len(conversation_ids), len(tags_list))
            conversation_ids = conversation_ids[:min_length]
            tags_list = tags_list[:min_length]

        return conversation_ids, tags_list

    def make_csv(self, data_list: List[str], output_file: str, header: str = 'Conversation ID') -> None:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([header])
            for item in data_list:
                writer.writerow([item])

    @abstractmethod
    def filter_conversations(self) -> Tuple[List[str], int]:
        raise NotImplementedError

    @abstractmethod
    def export_filtered_conversations(self, output_file: str) -> None:
        raise NotImplementedError
