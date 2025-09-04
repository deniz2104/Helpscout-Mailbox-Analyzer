from typing import Optional
from core_system import CoreSystem
import config
import time
from datetime import datetime
from get_last_month_dates import get_last_month_dates
    
class HelpScoutMailboxConversations:
    def __init__(self, client_id: str, client_secret: str):
        self.core_system_helper = CoreSystem(client_id, client_secret)

    def get_mailbox(self, page_number=1):
        return self.core_system_helper.make_request("conversations", params={
            "status": "active,open,closed",
            "mailbox": config.MAILBOX_ID,
            "page": page_number
        })

    def _get_creation_date(self, conversation_id) -> Optional[str]:
        conversation_data = self.core_system_helper.make_request(f"conversations/{conversation_id}")
        return conversation_data.get('createdAt') if conversation_data else None

    def _convert_creation_date(self, creation_date) -> str:
        return datetime.fromisoformat(str(creation_date)).strftime("%Y-%m-%d")

    def _filter_conversations_by_date(self, conversations: dict, start_date: str, end_date: str) -> dict:
        filtered_conversations = {}
        for conv_id, creation_date in conversations.items():
            if start_date <= self._convert_creation_date(creation_date) <= end_date:
                filtered_conversations[conv_id] = creation_date
            else: continue
        return filtered_conversations

    def analyze_last_month_conversations(self):
        start_date, end_date = get_last_month_dates()
        
        page = 1
        all_filtered_conversations = {}

        while True:
            conversations_data = self.get_mailbox(page_number=page)
            
            if not conversations_data or '_embedded' not in conversations_data:
                break
                
            conversations = conversations_data['_embedded']['conversations']
            if not conversations:
                break

            new_conversation = {}
            for conv in conversations:
                conv_id = conv['id']
                creation_date = self._get_creation_date(conv_id)

                new_conversation[conv_id] = creation_date

            filtered_conversations = self._filter_conversations_by_date(new_conversation, start_date, end_date)

            all_filtered_conversations.update(filtered_conversations)

            if not filtered_conversations and conversations:
                last_conv_date = self._get_creation_date(conversations[-1]['id'])
                if last_conv_date:
                    last_date = self._convert_creation_date(last_conv_date)
                    if last_date < start_date:
                        break

            page += 1
        
        return all_filtered_conversations


def main():
    client = HelpScoutMailboxConversations(config.CLIENT_ID, config.CLIENT_SECRET)

    start_time = time.time()
    conversations_dict = client.analyze_last_month_conversations()
    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
