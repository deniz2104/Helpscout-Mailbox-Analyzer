from mailbox_base import MailboxBase

class HelpscoutFreeMailboxConversations(MailboxBase):
    @property
    def mailbox_id(self) -> int:
        return MAILBOX_FREE_ID

    @property
    def csv_filename(self) -> str:
        return "filtered_free_conversations_ids.csv"

def main():
    helpscout_free_mailbox = HelpscoutFreeMailboxConversations(CLIENT_ID, CLIENT_SECRET)
    helpscout_free_mailbox.analyze_last_month_conversations()

if __name__ == "__main__":
    main()

