import csv
from HelperFiles.helper_file_to_make_csv_from_list import make_csv

class FilterWporgConversations():
    def __init__(self):
        self.ids_file = 'CSVs/filtered_free_conversations_ids.csv'
        self.tags_file = 'CSVs/filtered_free_conversations_tags.csv'
        self.target_tag = 'team reply'
        self.output_file = 'CSVs/filtered_wporg_conversations.csv'

    def _read_csv(self, file_path: str, is_tags: bool = False) -> list[int] | list[str]:
        data_list = []
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    if is_tags:
                        data_list.append(','.join(row).lower())
                    else:
                        data_list.append(int(row[0]))
        except FileNotFoundError:
            print(f"Error: {file_path} not found")
        return data_list

    def _get_conversation_data(self) -> tuple[list[int], list[str]]:
        conversation_ids: list[int] = self._read_csv(self.ids_file)  # type: ignore
        tags_list: list[str] = self._read_csv(self.tags_file, is_tags=True)  # type: ignore

        min_length = min(len(conversation_ids), len(tags_list))
        if len(conversation_ids) != len(tags_list):
            print(f"Warning: Mismatch in row counts. Using shortest length: {min_length}")

        return conversation_ids[:min_length], tags_list[:min_length]

    def _filter_by_tag(self, conversation_ids: list[int], tags_list: list[str]) -> list[int]:
        return [conv_id for conv_id, tags in zip(conversation_ids, tags_list) if self.target_tag in tags]

    def process_and_export(self) -> None:
        conversation_ids, tags_list = self._get_conversation_data()
        
        if not conversation_ids or not tags_list:
            print("Could not load necessary data. Creating empty output file.")
            make_csv([], self.output_file)
            return

        filtered_ids = self._filter_by_tag(conversation_ids, tags_list)

        if filtered_ids:
            make_csv(filtered_ids, self.output_file)
        else:
            print("No conversations found with the target tag. Creating empty output file.")
            make_csv([], self.output_file)

def main():
    filter_wporg = FilterWporgConversations()
    filter_wporg.process_and_export()

if __name__ == "__main__":
    main()