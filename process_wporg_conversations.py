from core_system import CoreSystem
import re
from helper_file_to_export_csvs_to_list import export_csv_to_list
from config_loader import get_helpscout_credentials, load_config

class ProcessWPOrgConversations():
    def __init__(self, client_id, client_secret):
        self.core_system_helper = CoreSystem(client_id, client_secret)
        self.processed_file = 'filtered_wporg_conversations.csv'
        self.dict_of_usernames = {}
        config = load_config()
        self.wp_org_usernames = list(config.get("WP_ORG_USERNAMES", {}).keys())
    
    def extract_username_from_body(self, body):
        if not body:
            return None
        
        match = re.search(r'(.+?)\s+wrote:', body)
        if match:
            return match.group(1).strip()
        return None

    def get_threads(self, conversation_id):
        return self.core_system_helper.make_request(f"conversations/{conversation_id}/threads")

    def get_a_conversation(self, conversation_id):
        return self.core_system_helper.make_request(f"conversations/{conversation_id}")
    
    def process_conversations(self):
        conversation_ids = export_csv_to_list(self.processed_file)
        for conversation_id in conversation_ids:
            threads = self.get_threads(conversation_id)
            
            if not threads or '_embedded' not in threads:
                print(f"No threads found for conversation ID {conversation_id}")
                continue
            
            for thread in threads['_embedded']['threads']:
                if thread.get('type') == 'customer' and 'body' in thread:
                    body = thread['body']
                    username_id = self.extract_username_from_body(body)
                    if username_id and username_id in self.wp_org_usernames:
                        self.dict_of_usernames[username_id] = self.dict_of_usernames.get(username_id, 0) + 1

        return self.dict_of_usernames


def main():
    client_id, client_secret = get_helpscout_credentials()
    processor = ProcessWPOrgConversations(client_id, client_secret)
    result = processor.process_conversations()

if __name__ == "__main__":
    main()

