from typing import List, Tuple
from conversation_filter_base import ConversationFilterBase

class FilterWporgConversations(ConversationFilterBase):
    def __init__(self):
        super().__init__(
            ids_file='filtered_free_conversations_ids.csv',
            tags_file='filtered_free_conversations_tags.csv',
            target_tag='wporg'
        )

    def filter_wporg_conversations(self) -> Tuple[List[str], List[str]]:
        return self.load_conversations_and_tags()

    def filter_conversations(self) -> Tuple[List[str], int]:
        conversation_ids, tags_list = self.load_conversations_and_tags()

        filtered_ids = []
        wporg_count = 0

        for conv_id, tags in zip(conversation_ids, tags_list):
            if self.target_tag in tags.lower():
                filtered_ids.append(conv_id)
                wporg_count += 1

        return filtered_ids, wporg_count

    def make_filtered_list(self) -> Tuple[List[str], int]:
        return self.filter_conversations()

    def export_filtered_conversations(self, output_file: str) -> None:
        filtered_ids, _ = self.filter_conversations()
        self.make_csv(filtered_ids, output_file)

def main():
    filter_wporg = FilterWporgConversations()
    filter_wporg.export_filtered_conversations('filtered_wporg_conversations.csv')

if __name__ == "__main__":
    main()
