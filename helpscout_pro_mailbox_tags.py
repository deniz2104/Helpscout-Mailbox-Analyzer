from mailbox_base import MailboxBase
class HelpscoutProMailboxTags(MailboxBase):
    @property
    def mailbox_id(self) -> int:
        return MAILBOX_PRO_ID

    @property
    def csv_filename(self) -> str:
        return "filtered_pro_conversations_tags.csv"
    

def main():
    helpscout_pro_mailbox = HelpscoutProMailboxTags(CLIENT_ID, CLIENT_SECRET)
    helpscout_pro_mailbox.analyze_last_month_tags()

if __name__ == "__main__":
    main()

