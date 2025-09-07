from mailbox_base import MailboxBase
from config import MAILBOX_OPTIMOLE_ID,CLIENT_ID, CLIENT_SECRET

class HelpscoutOptimoleMailboxConversations(MailboxBase):
    @property
    def mailbox_id(self) -> int:
        return MAILBOX_OPTIMOLE_ID

    @property
    def csv_filename(self) -> str:
        return "filtered_optimole_conversations_ids.csv"

def main():
    helpscout_optimole_mailbox = HelpscoutOptimoleMailboxConversations(CLIENT_ID, CLIENT_SECRET)
    helpscout_optimole_mailbox.analyze_last_month_conversations()

if __name__ == "__main__":
    main()

