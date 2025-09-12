import json
import os
from base_wporg_conversations import BaseConversations
from config_loader import get_helpscout_credentials
from helper_file_to_change_keys_from_wporg_username_to_team_member_names import map_wporg_usernames_to_names

class ProcessWPOrgConversations(BaseConversations):
    @property
    def processed_file(self) -> str:
        return 'CSVs/filtered_wporg_conversations.csv'
    
    @property
    def config_usernames_key(self) -> str:
        return 'WP_ORG_USERNAMES'

def main():
    client_id, client_secret = get_helpscout_credentials()
    processor = ProcessWPOrgConversations(client_id, client_secret)
    result = processor.process_conversations()
    
    mapped_result = map_wporg_usernames_to_names(result)
    
    os.makedirs("CSVs", exist_ok=True)
    with open("CSVs/process_wporg_results.json", "w", encoding="utf-8") as f:
        json.dump({"Wporg": mapped_result}, f, indent=2)

if __name__ == "__main__":
    main()
