from mailbox_base import MailboxBase
from config import MAILBOX_OPTIMOLE_ID, CLIENT_ID, CLIENT_SECRET
class HelpscoutOptimoLeMailboxTags(MailboxBase):
    @property
    def mailbox_id(self) -> int:
        return MAILBOX_OPTIMOLE_ID

    @property
    def csv_filename(self) -> str:
        return "filtered_optimole_conversations_tags.csv"


def main():
    helpscout_optimo_le_mailbox = HelpscoutOptimoLeMailboxTags(CLIENT_ID, CLIENT_SECRET)
    helpscout_optimo_le_mailbox.analyze_last_month_tags()

if __name__ == "__main__":
    main()

