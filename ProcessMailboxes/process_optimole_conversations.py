import json
import os
from typing import Optional

from BaseClasses.base_wporg_conversations import BaseConversations
from CredentialsAndJsonManager.config_loader import get_helpscout_credentials
from BaseClasses.conversation_tag_base import ConversationTagBase
from HelperFiles.helper_file_to_change_keys_from_wporg_username_to_team_member_names import map_wporg_usernames_to_names

class ProcessOptimoleConversations(BaseConversations, ConversationTagBase):
    def __init__(self, client_id: str, client_secret: str):
        BaseConversations.__init__(self, client_id, client_secret)
        ConversationTagBase.__init__(self, client_id, client_secret)

    def _get_core_system_helper(self):
        return self.core_system_helper

    @property
    def processed_file(self) -> str:
        return "CSVs/filtered_optimole_conversations_no_replies.csv"
    
    @property
    def processed_file_for_tags(self) -> str:
        return "CSVs/filtered_optimole_conversations.csv"

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
    result1 = processor.process_conversations()
    result2 = processor.categorise_filtered_conversations()

    mapped_result = map_wporg_usernames_to_names(result1)

    os.makedirs("CSVs", exist_ok=True)
    with open("CSVs/process_optimole_results.json", "w", encoding="utf-8") as f:
        result2["Wporg Optimole"] = mapped_result
        json.dump(result2, f, indent=2)

if __name__ == "__main__":
    main()
