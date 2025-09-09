from base_wporg_conversations import BaseWporgConversations
from config_loader import get_helpscout_credentials

class ProcessWPOrgConversations(BaseWporgConversations):
    @property
    def processed_file(self) -> str:
        return 'CSVs/filtered_wporg_conversations.csv'
    
    @property
    def config_usernames_key(self) -> str:
        return 'WP_ORG_USERNAMES'

def main():
    client_id, client_secret = get_helpscout_credentials()
    processor = ProcessWPOrgConversations(client_id, client_secret)
    processor.dict_of_usernames = processor.process_conversations()
    print(processor.dict_of_usernames)
    
if __name__ == "__main__":
    main()
