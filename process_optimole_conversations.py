##TODO  : take into consideration just the tags (wp-media-library,team reply for wporg (similar approach to process_wporg_conversations) and other are optimole general things that does not require tags)
from base_wporg_conversations import BaseWporgConversations
from config_loader import get_helpscout_credentials

class ProcessOptimoleConversations(BaseWporgConversations):
    @property
    def processed_file(self) -> str:
        return 'CSVs/filtered_optimole_conversations_no_replies.csv'
    
    @property  
    def config_usernames_key(self) -> str:
        return 'WP_ORG_USERNAMES'
    
def main():
    client_id, client_secret = get_helpscout_credentials()
    processor = ProcessOptimoleConversations(client_id, client_secret)
    processor.dict_of_usernames = processor.process_conversations()
    
if __name__ == "__main__":
    main()

