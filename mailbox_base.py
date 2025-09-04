from abc import ABC, abstractmethod
from typing import Optional
import csv
from datetime import datetime
from core_system import CoreSystem


class MailboxBase(ABC):
    """Abstract base class for HelpScout mailbox operations."""
    
    def __init__(self, client_id: Optional[str], client_secret: Optional[str]):
        if not client_id or not client_secret:
            raise ValueError("CLIENT_ID and CLIENT_SECRET must be provided")
        self.core_system_helper = CoreSystem(client_id, client_secret)

    @property
    @abstractmethod
    def mailbox_id(self) -> str:
        """Return the specific mailbox ID for this implementation."""
        pass

    @property
    @abstractmethod
    def csv_filename(self) -> str:
        """Return the CSV filename for this mailbox type."""
        pass

    def get_mailbox(self, page_number=1):
        """Get conversations from the mailbox."""
        return self.core_system_helper.make_request("conversations", params={
            "status": "active,open,closed",
            "mailbox": self.mailbox_id,
            "page": page_number
        })

    def get_creation_date(self, conversation_id) -> Optional[str]:
        """Get the creation date of a conversation."""
        conversation_data = self.core_system_helper.make_request(f"conversations/{conversation_id}")
        return conversation_data.get('createdAt') if conversation_data else None

    def _convert_creation_date(self, creation_date) -> str:
        """Convert ISO format date to YYYY-MM-DD format."""
        return datetime.fromisoformat(str(creation_date)).strftime("%Y-%m-%d")
    
    def _is_in_specified_date_range(self, creation_date: str, start_date: str, end_date: str) -> bool:
        """Check if a creation date falls within the specified date range."""
        if not creation_date:
            return False
        
        conv_date = self._convert_creation_date(creation_date)
        return start_date <= conv_date <= end_date

    def export_list_to_csv(self, conversation_ids: list, file_path: str, write_header: bool = False) -> None:
        """Export conversation IDs to a CSV file."""
        mode = 'w' if write_header else 'a'
        with open(file_path, mode, newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if write_header:
                writer.writerow(['Conversation ID'])
            
            for conv_id in conversation_ids:
                writer.writerow([conv_id])

    def analyze_last_month_conversations(self):
        """Analyze and export conversations from the last month."""
        from get_last_month_dates import get_last_month_dates
        
        start_date, end_date = get_last_month_dates()

        def get_conversation_date(position):
            conversation_data = self.get_creation_date(conversations[position]['id'])
            return self._convert_creation_date(conversation_data) if conversation_data else None
     
        page = 1
        first_page = True

        while True:
            conversations_data = self.get_mailbox(page_number=page)
            
            if not conversations_data or '_embedded' not in conversations_data:
                break
                
            conversations = conversations_data['_embedded']['conversations']
            if not conversations:
                break

            first_conversation_date = get_conversation_date(0)
            if first_conversation_date and first_conversation_date > end_date:
                page += 1
                continue

            last_conversation_date = get_conversation_date(-1)
            if last_conversation_date and last_conversation_date < start_date:
                break

            list_of_ids = [conv['id'] for conv in conversations]
            self.export_list_to_csv(list_of_ids, self.csv_filename, write_header=first_page)

            first_page = False
            page += 1
