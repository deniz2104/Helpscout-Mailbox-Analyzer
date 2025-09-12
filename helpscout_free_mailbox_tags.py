from mailbox_base import MailboxBase
from config_loader import get_helpscout_credentials, load_config

class HelpscoutFreeMailboxTags(MailboxBase):
    @property
    def mailbox_id(self) -> int:
        config = load_config()
        return config["MAILBOX_FREE_ID"]

    @property
    def csv_filename(self) -> str:
        return "CSVs/filtered_free_conversations_tags.csv"


def main():
    client_id, client_secret = get_helpscout_credentials()
    helpscout_free_mailbox = HelpscoutFreeMailboxTags(client_id, client_secret)
    helpscout_free_mailbox.analyze_last_month_tags()

if __name__ == "__main__":
    main()

