from abc import ABC, abstractmethod
from collections import Counter
import re
from core_system import CoreSystem
from helper_file_to_export_csvs_to_list import export_csv_to_list
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

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
        usernames = set(self.load_usernames_from_config())
        conversation_ids = export_csv_to_list(self.processed_file)

        def process_single_conversation(conv_id):
            threads = self.get_threads(conv_id)
            if not threads or '_embedded' not in threads:
                return []
            return [
                self.extract_username_from_body(thread['body'])
                for thread in threads['_embedded']['threads']
                if self.should_process_thread(thread) and 'body' in thread
            ]

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(process_single_conversation, conversation_ids)

        extracted_usernames = (u for conv_users in results for u in conv_users)
        filtered_usernames = filter(lambda u: u and u in usernames, extracted_usernames)

        return dict(Counter(filtered_usernames))