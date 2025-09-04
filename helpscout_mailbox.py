import csv
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
    
    def _is_in_specified_date_range(self, creation_date: str, start_date: str, end_date: str) -> bool:
        if not creation_date:
            return False
        
        conv_date = self._convert_creation_date(creation_date)
        return start_date <= conv_date <= end_date
    
    def export_to_csv(self, conversations : dict, file_path: str,start_date,end_date, write_header: bool = False) -> None:
        mode = 'w' if write_header else 'a'
        with open(file_path, mode, newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if write_header:
                writer.writerow(['Conversation ID', 'Creation Date'])
            for conversation_id, creation_date in conversations.items():
                if self._is_in_specified_date_range(creation_date, start_date, end_date):
                    writer.writerow([conversation_id, self._convert_creation_date(creation_date)])

    def analyze_last_month_conversations(self):
        start_date, end_date = get_last_month_dates()
        
        page = 1
        first_page = True

        while True:
            conversations_data = self.get_mailbox(page_number=page)
            
            if not conversations_data or '_embedded' not in conversations_data:
                break
                
            conversations = conversations_data['_embedded']['conversations']
            if not conversations:
                break

            first_conversation_date = self._get_creation_date(conversations[0]['id'])
            if first_conversation_date:
                first_date = self._convert_creation_date(first_conversation_date)
                if first_date >= end_date:
                    print(f"Page {page}: Skipping - conversations too new (newest: {first_date} > {end_date})")
                    page += 1
                    continue

            last_conversation_date = self._get_creation_date(conversations[-1]['id'])
            if last_conversation_date:
                last_date = self._convert_creation_date(last_conversation_date)
                if last_date <= start_date:
                    print(f"Page {page}: Stopping - conversations too old (oldest: {last_date} < {start_date})")
                    break

            new_conversation = {}
            for conv in conversations:
                conv_id = conv['id']
                creation_date = self._get_creation_date(conv_id)
                new_conversation[conv_id] = creation_date

            self.export_to_csv(new_conversation,"filtered_conversations.csv", start_date, end_date, write_header=first_page)
            first_page = False
            page += 1

def main():
    client = HelpScoutMailboxConversations(config.CLIENT_ID, config.CLIENT_SECRET)

    start_time = time.time()
    client.analyze_last_month_conversations()
    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
