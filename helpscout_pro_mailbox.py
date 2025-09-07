from mailbox_base import MailboxBase
from config import CLIENT_ID, CLIENT_SECRET, MAILBOX_PRO_ID

class HelpScoutProMailboxConversations(MailboxBase):
    @property
    def mailbox_id(self) -> int:
        return MAILBOX_PRO_ID

    @property
    def csv_filename(self) -> str:
        return "filtered_pro_conversations_ids.csv"
    
def main():
    helpscout_pro_mailbox = HelpScoutProMailboxConversations(CLIENT_ID, CLIENT_SECRET)
    helpscout_pro_mailbox.analyze_last_month_conversations()

if __name__ == "__main__":
    main()
