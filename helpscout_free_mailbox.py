from mailbox_base import MailboxBase
import config 

class HelpscoutFreeMailboxConversations(MailboxBase):
    @property
    def mailbox_id(self) -> str:
        return str(config.MAILBOX_FREE_ID)

    @property
    def csv_filename(self) -> str:
        return "filtered_free_conversations_ids.csv"
    
if __name__ == "__main__":
    client = HelpscoutFreeMailboxConversations(config.CLIENT_ID, config.CLIENT_SECRET)
    client.analyze_last_month_conversations()
    print("Free mailbox conversations exported successfully!")
