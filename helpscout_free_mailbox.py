from mailbox_base import MailboxBase
from config import MAILBOX_FREE_ID, CLIENT_ID, CLIENT_SECRET

class HelpscoutFreeMailboxConversations(MailboxBase):
    @property
    def mailbox_id(self) -> int:
        return MAILBOX_FREE_ID

    @property
    def csv_filename(self) -> str:
        return "filtered_free_conversations_ids.csv"
    
    def get_conversation(self):
        conversations_data = self.get_mailbox(self.mailbox_id)
        if not conversations_data or '_embedded' not in conversations_data:
            return []
        conversations = conversations_data['_embedded']['conversations']

        return conversations

def main():
    client = HelpscoutFreeMailboxConversations(CLIENT_ID, CLIENT_SECRET)
    client.analyze_last_month_conversations()

if __name__ == "__main__":
    main()

