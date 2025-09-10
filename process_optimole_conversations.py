from typing import Optional

from base_wporg_conversations import BaseConversations
from config_loader import get_helpscout_credentials
from conversation_tag_base import ConversationTagBase

class ProcessOptimoleConversations(BaseConversations, ConversationTagBase):
    def __init__(self, client_id: str, client_secret: str):
        BaseConversations.__init__(self, client_id, client_secret)
        ConversationTagBase.__init__(self, client_id, client_secret)

    def _get_core_system_helper(self):
        return self.core_system_helper  # Already initialized in BaseConversations

    @property
    def processed_file(self) -> str:
        return "CSVs/filtered_optimole_conversations_no_replies.csv"
    
    @property
    def processed_file_for_tags(self) -> str:
        return "CSVs/filtered_optimole_conversations_ids.csv"

    @property
    def config_usernames_key(self) -> str:
        return "WP_ORG_USERNAMES"

    def _get_category(self, product_or_plugin: Optional[str]) -> str:
        return product_or_plugin if product_or_plugin else "General Optimole"

    def categorise_filtered_conversations(self) -> dict:
        if "General Optimole" not in self.dictionary_of_tag_and_names:
            self.dictionary_of_tag_and_names["General Optimole"] = {}

        return super().categorise_filtered_conversations()

def main():
    client_id, client_secret = get_helpscout_credentials()
    processor = ProcessOptimoleConversations(client_id, client_secret)
    processor.dict_of_usernames = processor.process_conversations()
    categorized_results = processor.categorise_filtered_conversations()
    processor.dictionary_of_tag_and_names = categorized_results

if __name__ == "__main__":
    main()
