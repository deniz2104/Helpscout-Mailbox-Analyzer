from abc import ABC, abstractmethod
import re
from core_system import CoreSystem
from helper_file_to_export_csvs_to_list import export_csv_to_list
from typing import Optional

class BaseWporgConversations(ABC):
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.core_system_helper = CoreSystem(client_id, client_secret)
        self.dict_of_usernames = {}
    
    @property
    @abstractmethod
    def processed_file(self) -> str:
        """Return the CSV file path containing filtered conversation IDs."""
        pass
    
    @property
    @abstractmethod
    def config_usernames_key(self) -> str:
        """Return the config key for usernames (e.g., 'WP_ORG_USERNAMES')."""
        pass
    
    def extract_username_from_body(self, body: str) -> Optional[str]:
        """Extract username from conversation body. Implementation may vary by type."""
        match = re.search(r'(.+?)\s+wrote:', body)
        if match:
            return match.group(1).strip()
        return None
    
    def should_process_thread(self, thread: dict) -> bool:
        """Determine if a thread should be processed based on specific criteria."""
        return thread.get('type') == 'customer'
    
    def get_threads(self, conversation_id):
        """Get threads for a conversation."""
        return self.core_system_helper.make_request(f"conversations/{conversation_id}/threads")
    
    def load_usernames_from_config(self):
        """Load usernames from config using the specific config key."""
        from config_loader import load_config
        config = load_config()
        return list(config.get(self.config_usernames_key, {}).keys())
    
    def process_conversations(self):
        """Process conversations and count username occurrences."""
        usernames = self.load_usernames_from_config()
        conversation_ids = export_csv_to_list(self.processed_file)
        
        for conversation_id in conversation_ids:
            threads = self.get_threads(conversation_id)
            
            if not threads or '_embedded' not in threads:
                print(f"No threads found for conversation ID {conversation_id}")
                continue
            
            for thread in threads['_embedded']['threads']:
                if self.should_process_thread(thread) and 'body' in thread:
                    body = thread['body']
                    username_id = self.extract_username_from_body(body)
                    if username_id and username_id in usernames:
                        self.dict_of_usernames[username_id] = self.dict_of_usernames.get(username_id, 0) + 1

        return self.dict_of_usernames