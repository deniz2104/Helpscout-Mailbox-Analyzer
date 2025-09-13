from BaseClasses.mailbox_base import MailboxBase
from CredentialsAndJsonManager.config_loader import get_helpscout_credentials, load_config

class HelpScoutProMailboxConversations(MailboxBase):
    @property
    def mailbox_id(self) -> int:
        config = load_config()
        return config["MAILBOX_PRO_ID"]

    @property
    def csv_filename(self) -> str:
        return "CSVs/filtered_pro_conversations_ids.csv"
    
def main():
    client_id, client_secret = get_helpscout_credentials()
    helpscout_pro_mailbox = HelpScoutProMailboxConversations(client_id, client_secret)
    helpscout_pro_mailbox.analyze_last_month_conversations()

if __name__ == "__main__":
    main()
