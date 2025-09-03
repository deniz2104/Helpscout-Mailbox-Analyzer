from typing import Optional
import requests
from get_access_token import GetAccessToken
import config
from datetime import datetime
from pprint import pprint
    
class HelpScoutClient:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id :str = client_id
        self.client_secret :str = client_secret
        self.access_token :Optional[str] = None
        self.token_manager = GetAccessToken(client_id, client_secret)

        self.base_url :str = "https://api.helpscout.net/v2"

    def make_request(self, endpoint: str, params: Optional[dict] = None) -> Optional[dict]:
        if not self.token_manager.ensure_valid_token():
            return None
        
        self.access_token = self.token_manager.access_token
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{self.base_url}/{endpoint}", headers=headers, params=params)
        return response.json() if response.status_code == 200 else None


    def get_mailbox(self,page_number=1):
        return self.make_request("conversations", params={
            "status": "active,open,closed",
            "mailbox": config.MAILBOX_ID,
            "page": page_number
        })
    
    def get_all_the_tags(self):
        return self.make_request("tags")

    def _get_creation_date(self, conversation_id) -> Optional[str]:
        conversation_data = self.make_request(f"conversations/{conversation_id}")
        return conversation_data.get('createdAt') if conversation_data else None

    def _get_conversation_tags(self, conversation_id) -> list[dict[str, str]]:
        conversation_data = self.make_request(f"conversations/{conversation_id}")
        return conversation_data.get('tags', []) if conversation_data else []

    def _preprocess_tags(self, conversation_id) -> list[str]:
        tag_list = self._get_conversation_tags(conversation_id)
        return [tag['tag'] for tag in tag_list]

    def _get_conversation_threads(self, conversation_id) -> Optional[dict]:
        return self.make_request(f"conversations/{conversation_id}/threads")

    def _convert_creation_date(self, creation_date) -> Optional[str]:
        return datetime.fromisoformat(str(creation_date)).strftime("%Y-%m-%d") if creation_date else None

    def _get_staff_responses(self, conversation_id) -> dict[str, int]:
        threads_data = self._get_conversation_threads(conversation_id)
        staff_counts :dict[str,int] = {}
        
        if not threads_data or '_embedded' not in threads_data:
            return staff_counts
            
        for thread in threads_data['_embedded']['threads']:
            created_by = thread.get('createdBy', {})
            if created_by.get('type') == 'user' and created_by.get('id', 0) > 1:
                staff_name = f"{created_by.get('first', '')} {created_by.get('last', '')}".strip()
                
                if staff_name and staff_name != "Help Scout" and staff_name != "Buddy (Themeisle)":
                    staff_counts[staff_name] = staff_counts.get(staff_name, 0) + 1

        return staff_counts
    
    def _print_conversation_details(self, i, conv):
        print(f"#{i} - Conversation #{conv['number']} | Status: {conv['status'].upper()}")
        print(f"Subject: {conv['subject'][:60]}...")
        
        staff_counts = self._get_staff_responses(conv['id'])
        creation_date = self._convert_creation_date(self._get_creation_date(conv['id']))
        tags = self._preprocess_tags(conv['id'])
        
        if staff_counts:
            staff_list = [f"{staff} ({count} replies)" for staff, count in staff_counts.items()]
            print(f"Staff who responded: {', '.join(staff_list)}")
            print(f"Created At: {creation_date if creation_date else 'N/A'}")
            print(f"Tags: {', '.join(tags) if tags else 'No tags'}")
        else:
            print("Staff who responded: No staff responses yet")
        
        print("-" * 80)
        return staff_counts

    def analyze_conversations(self, conversations_data):
        if not conversations_data or '_embedded' not in conversations_data:
            print("No conversation data found")
            return
        
        conversations = conversations_data['_embedded']['conversations']
        
        print("=== WHO RESPONDED TO CONVERSATIONS ===")

        for i, conv in enumerate(conversations, 1):
            self._print_conversation_details(i, conv)

def main():
    client = HelpScoutClient(config.CLIENT_ID, config.CLIENT_SECRET)
    
    print("Fetching conversation data (all pages)...")
    page=1
    while True:
        conversations_data = client.get_mailbox(page_number=page)
        client.analyze_conversations(conversations_data)
        page += 1

if __name__ == "__main__":
    main()
