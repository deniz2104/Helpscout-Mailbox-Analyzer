import csv
import os

class FilterWporgConversations:
    def __init__(self):
        self.ids_file = 'filtered_free_conversations_ids.csv'
        self.tags_file = 'filtered_free_conversations_tags.csv'

    def make_list_from_csv(self, file_path, is_tags=False):
        data_list = []
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if row:  
                    data_list.append(row[0])
                elif is_tags:
                    data_list.append('')
        return data_list

    def filter_wporg_conversations(self):
        if not os.path.exists(self.ids_file):
            print(f"Error: {self.ids_file} not found")
            return [], []

        if not os.path.exists(self.tags_file):
            print(f"Error: {self.tags_file} not found")
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

    def make_filtered_list(self):
        conversation_ids, tags_list = self.filter_wporg_conversations()

        filtered_ids = []
        wporg_count = 0

        for conv_id, tags in zip(conversation_ids, tags_list):
            if 'wporg' in tags.lower():
                filtered_ids.append(conv_id)
                wporg_count += 1

        return filtered_ids, wporg_count

    def make_csv(self, filtered_ids, output_file):
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Conversation ID'])
            for conv_id in filtered_ids:
                writer.writerow([conv_id])

def main():
    filter_wporg = FilterWporgConversations()
    filtered_ids, _ = filter_wporg.make_filtered_list()
    filter_wporg.make_csv(filtered_ids, 'filtered_wporg_conversations.csv')

if __name__ == "__main__":
    main()
