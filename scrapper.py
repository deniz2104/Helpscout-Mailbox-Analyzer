import requests
from get_access_token import GetAccessToken
import config
    
class HelpScoutClient:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_manager = GetAccessToken(client_id, client_secret)

        self.base_url = "https://api.helpscout.net/v2"
    
    def make_request(self, endpoint, params=None):
        if not self.token_manager.ensure_valid_token():
            return None
        
        self.access_token = self.token_manager.access_token
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{self.base_url}/{endpoint}", headers=headers, params=params)
        return response.json() if response.status_code == 200 else None
    
    def get_mailbox(self):
        return self.make_request("conversations", params={
            "status": "active,open,closed", 
            "mailbox": config.MAILBOX_ID
        })

    def get_conversation_threads(self, conversation_id):
        return self.make_request(f"conversations/{conversation_id}/threads")
    
    def get_thread_details(self, conversation_id, thread_id):
        return self.make_request(f"conversations/{conversation_id}/threads/{thread_id}")
    
    def _get_staff_responses(self, conversation_id):
        threads_data = self.get_conversation_threads(conversation_id)
        staff_counts = {}
        
        if not threads_data or '_embedded' not in threads_data:
            return staff_counts
            
        for thread in threads_data['_embedded']['threads']:
            created_by = thread.get('createdBy', {})
            if created_by.get('type') == 'user' and created_by.get('id', 0) > 1:
                staff_name = f"{created_by.get('first', '')} {created_by.get('last', '')}".strip()
                
                if staff_name and staff_name != "Help Scout":
                    staff_counts[staff_name] = staff_counts.get(staff_name, 0) + 1

        return staff_counts
    
    def _print_conversation_details(self, i, conv):
        print(f"#{i} - Conversation #{conv['number']} | Status: {conv['status'].upper()}")
        print(f"Subject: {conv['subject'][:60]}...")
        
        staff_counts = self._get_staff_responses(conv['id'])
            
        if staff_counts:
            staff_list = [f"{staff} ({count} replies)" for staff, count in staff_counts.items()]
            print(f"Staff who responded: {', '.join(staff_list)}")
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
    
    print("Fetching conversation data...")
    conversations_data = client.get_mailbox()
    
    if conversations_data:
        print("Analyzing conversations - who responded...")
        client.analyze_conversations(
            conversations_data
        )
    else:
        print("Failed to fetch conversation data")


if __name__ == "__main__":
    main()
