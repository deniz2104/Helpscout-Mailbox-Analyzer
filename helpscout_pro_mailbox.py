from mailbox_base import MailboxBase
import config

class HelpScoutProMailboxConversations(MailboxBase):
    @property
    def mailbox_id(self) -> str:
        return str(config.MAILBOX_PRO_ID)

    @property
    def csv_filename(self) -> str:
        return "filtered_pro_conversations_ids.csv"

def main():
    client = HelpScoutProMailboxConversations(config.CLIENT_ID, config.CLIENT_SECRET)
    client.analyze_last_month_conversations()
    
if __name__ == "__main__":
    main()
