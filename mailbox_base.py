from abc import ABC, abstractmethod
from typing import Optional, List, Any, Callable
import csv
import os
from datetime import datetime
from core_system import CoreSystem
from get_last_month_dates import get_last_month_dates

class MailboxBase(ABC):
    """Abstract base class for HelpScout mailbox operations."""

    def __init__(self, client_id: Optional[str], client_secret: Optional[str]):
        if not client_id or not client_secret:
            raise ValueError("CLIENT_ID and CLIENT_SECRET must be provided")
        self.core_system_helper = CoreSystem(client_id, client_secret)

    @property
    @abstractmethod
    def mailbox_id(self) -> int:
        """Return the specific mailbox ID for this implementation."""
        pass

    @property
    @abstractmethod
    def csv_filename(self) -> str:
        """Return the CSV filename for this mailbox type."""
        pass

    def _get_conversations_page(self, page_number: int) -> Optional[dict]:
        """Helper to get a single page of conversations."""
        return self.core_system_helper.make_request("conversations", params={
            "status": "active,open,closed",
            "mailbox": self.mailbox_id,
            "page": page_number
        })

    def _get_conversation_data(self, conversation_id: int) -> Optional[dict]:
        """Helper to get full data for a single conversation."""
        return self.core_system_helper.make_request(f"conversations/{conversation_id}")

    def _convert_creation_date(self, creation_date: str) -> str:
        """Convert ISO format date to YYYY-MM-DD HH:MM:SS format."""
        return datetime.fromisoformat(creation_date).strftime("%Y-%m-%d %H:%M:%S")

    def export_list_to_csv(self, data: List[Any], header: List[str], file_path: str, write_header: bool = False) -> None:
        """Export a list of data to a CSV file."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        mode = 'w' if write_header else 'a'
        with open(file_path, mode, newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if write_header:
                writer.writerow(header)
            writer.writerows(data)

    def _process_conversations_in_range(self, start_date: str, end_date: str, process_func: Callable[[List[dict], bool], None]):
        """Iterates through conversations and processes them if they are within the date range."""
        page = 1
        is_first_page_write = True

        while True:
            conversations_data = self._get_conversations_page(page_number=page)
            if conversations_data is None:
                print(f"Warning: Could not retrieve conversations for page {page}")
                break
            conversations = conversations_data.get('_embedded', {}).get('conversations', [])

            if not conversations:
                break

            latest_conv_date = self.get_creation_date(conversations[0]['id'])
            earliest_conv_date = self.get_creation_date(conversations[-1]['id'])

            if latest_conv_date and latest_conv_date > end_date:
                page += 1
                continue
            
            if earliest_conv_date and earliest_conv_date < start_date:
                break

            if is_first_page_write:
                conversation_ids = [conv['id'] for conv in conversations]
                valid_ids = []
                for conv_id in conversation_ids:
                    creation_date = self.get_creation_date(conv_id)
                    if creation_date and start_date <= creation_date <= end_date:
                        valid_ids.append(conv_id)
                conversations_to_process = [conv for conv in conversations if conv['id'] in valid_ids]

                if conversations_to_process:
                    process_func(conversations_to_process, is_first_page_write)
                    is_first_page_write = False

                page += 1
                continue

            process_func(conversations, is_first_page_write)
            page += 1

    def get_creation_date(self, conversation_id: int) -> Optional[str]:
        conversation_data = self._get_conversation_data(conversation_id)
        if conversation_data is None:
            print(f"Warning: Could not retrieve data for conversation {conversation_id}")
            return None
        created_at = conversation_data.get('createdAt')
        return self._convert_creation_date(created_at) if created_at else None

    def analyze_last_month_tags(self) -> None:
        start_date, end_date = get_last_month_dates()

        def process_and_export_tags(conversations: List[dict], write_header: bool):
            tags_data = [[tag['tag'] for tag in conv.get('tags', [])] for conv in conversations]
            self.export_list_to_csv(tags_data, ['Tags'], self.csv_filename, write_header)
        
        self._process_conversations_in_range(start_date, end_date, process_and_export_tags)

    def analyze_last_month_conversations(self) -> None:
        start_date, end_date = get_last_month_dates()

        def process_and_export_ids(conversations: List[dict], write_header: bool):
            ids_data = [[conv['id']] for conv in conversations]
            self.export_list_to_csv(ids_data, ['Conversation ID'], self.csv_filename, write_header)

        self._process_conversations_in_range(start_date, end_date, process_and_export_ids)