from mailbox_base import MailboxBase
class HelpscoutFreeMailboxTags(MailboxBase):
    @property
    def mailbox_id(self) -> int:
        return MAILBOX_FREE_ID

    @property
    def csv_filename(self) -> str:
        return "filtered_free_conversations_tags.csv"


def main():
    helpscout_free_mailbox = HelpscoutFreeMailboxTags(CLIENT_ID, CLIENT_SECRET)
    helpscout_free_mailbox.analyze_last_month_tags()

if __name__ == "__main__":
    main()

