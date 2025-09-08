from typing import List, Tuple
from conversation_filter_base import ConversationFilterBase

class FilterWporgConversations(ConversationFilterBase):
    def __init__(self):
        super().__init__(
            ids_file='filtered_free_conversations_ids.csv',
            tags_file='filtered_free_conversations_tags.csv'
        )
        self.target_tag = 'team reply'

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
        self.make_csv(filtered_ids, output_file)

def main():
    filter_wporg = FilterWporgConversations()
    filter_wporg.export_filtered_conversations('filtered_wporg_conversations.csv')

if __name__ == "__main__":
    main()
