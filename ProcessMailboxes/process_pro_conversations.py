import json
import os
from typing import Optional
from APIConnection.core_system import CoreSystem
from CredentialsAndJsonManager.config_loader import get_helpscout_credentials
from BaseClasses.conversation_tag_base import ConversationTagBase

class ProcessProConversations(ConversationTagBase):
    def _get_core_system_helper(self):
        return CoreSystem(self.client_id, self.client_secret)

    @property
    def processed_file_for_tags(self) -> str:
        return "CSVs/filtered_pro_conversations_ids.csv"

    def _get_category(self, product_or_plugin: Optional[str]) -> str:
        return product_or_plugin if product_or_plugin else "Others"

    def categorise_filtered_conversations(self) -> dict:
        if "Others" not in self.dictionary_of_tag_and_names:
            self.dictionary_of_tag_and_names["Others"] = {}

        return super().categorise_filtered_conversations()

def main():
    client_id, client_secret = get_helpscout_credentials()
    processor = ProcessProConversations(client_id, client_secret)
    result = processor.categorise_filtered_conversations()
    
    os.makedirs("CSVs", exist_ok=True)
    with open("CSVs/process_pro_results.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        
if __name__ == "__main__":
    main()
