from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime
from collections import defaultdict
from CredentialsAndJsonManager.config_loader import load_config
from HelperFiles.helper_file_to_export_csvs_to_list import export_csv_to_list
from Database.database_schema import get_connection
from HelperFiles.get_last_month_dates import get_last_month_dates

class ConversationTagBase(ABC):
    def __init__(self, client_id, client_secret):
        self.client_id :str = client_id
        self.client_secret : str= client_secret
        self.dictionary_of_tag_and_names = defaultdict(lambda: defaultdict(int))

        config = load_config()
        self.team_members :set[str] = set(config.get("TEAM_MEMBERS", {}).values())

        self.core_system_helper = self._get_core_system_helper()

        start_str, end_str = get_last_month_dates()
        self.start_date : datetime = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
        self.end_date : datetime = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")

    def _parse_helpscout_date(self, date_str: str) -> datetime:
        """Parse Helpscout date string to datetime object."""
        date_str = date_str.rstrip("Z")
        try:
            return datetime.fromisoformat(date_str)
        except ValueError:
            fmt = "%Y-%m-%dT%H:%M:%S.%f" if "." in date_str else "%Y-%m-%dT%H:%M:%S"
            return datetime.strptime(date_str, fmt)

    @abstractmethod
    def _get_core_system_helper(self):
        """Return an instance of CoreSystem."""
        pass

    @property
    @abstractmethod
    def processed_file_for_tags(self) -> str:
        """Return the CSV file path containing filtered conversation IDs for tagging."""
        pass

    def _get_threads(self, conversation_id: int) -> Optional[dict]:
        """Get threads for a conversation."""
        return self.core_system_helper.make_request(
            f"conversations/{conversation_id}/threads"
        )

    def _check_conversation_for_replies(
        self, dictionary_of_tags_and_names: dict, conversation_id: int, product_or_plugin: Optional[str] = None
    ) -> None:
        """Check conversation threads for replies from team members and categorize them."""
        threads = self._get_threads(conversation_id)
        if not threads or "_embedded" not in threads:
            print(f"No threads found for conversation ID {conversation_id}")
            return

        for thread in threads["_embedded"].get("threads", []):
            """ Check if the thread is a customer reply and the reply is in specified date range """
            created_by = thread.get("createdBy", {})
            created_at = thread.get("createdAt", "")
            type_of_thread = thread.get("type", "")
            if not created_at:
                continue

            try:
                thread_date = self._parse_helpscout_date(created_at)
            except Exception as e:
                print(f"Error parsing date {created_at}: {e}")
                continue

            is_in_range = self.start_date < thread_date < self.end_date
            
            if not is_in_range:
                continue

            """ Check if the thread was created by a team member """
            if created_by.get("type") == "user" and created_by.get("id", 0) > 1 and type_of_thread == "message":
                full_name = f"{created_by.get('first', '')} {created_by.get('last', '')}".strip()
                if full_name in self.team_members:
                    category = self._get_category(product_or_plugin)
                    """ Check if the category exists in the dictionary """
                    if category not in dictionary_of_tags_and_names:
                        dictionary_of_tags_and_names[category] = {}
                    """ Initialize the count for the full name if not already present """
                    if full_name not in dictionary_of_tags_and_names[category]:
                        dictionary_of_tags_and_names[category][full_name] = 0
                    dictionary_of_tags_and_names[category][full_name] += 1

    @abstractmethod
    def _get_category(self, product_or_plugin: str | None) -> str:
        """Determine the category based on product or plugin name."""
        pass

    def _validate_tag(self, list_of_tags: list[str]) -> Optional[str]:
        """Validate tags against the database and return the associated product name."""
        if not list_of_tags:
            return None

        query = """
            SELECT p.name
            FROM products p
            JOIN tags t ON p.id = t.product_id
            WHERE t.name IN ({})
        """.format(",".join("?" * len(list_of_tags)))

        """Execute the query and fetch the result."""
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query, list_of_tags)
            row = cursor.fetchone()

        """Return the product name if found, else None."""
        return row[0] if row else None

    def _get_conversation_data(self, conversation_id: int) -> Optional[dict]:
        """Get conversation data"""
        return self.core_system_helper.make_request(f"conversations/{conversation_id}")

    def _get_tags_from_conversation(self, conversation: dict) -> list[str]:
        """Extract tags from conversation data."""
        return [tag["tag"] for tag in conversation.get("tags", []) if "tag" in tag]

    def categorise_filtered_conversations(self) -> dict:
        """Process filtered conversations and categorize them by tags and team member replies."""
        filtered_ids : list[int] = export_csv_to_list(self.processed_file_for_tags)

        for conv_id in filtered_ids:
            conversation_data = self._get_conversation_data(conv_id)
            if not conversation_data:
                print(f"No data found for conversation {conv_id}")
                continue

            """ Extract tags and validate product name """
            tags_of_the_conversation : list[str] = self._get_tags_from_conversation(conversation_data)
            product_name : str | None = self._validate_tag(tags_of_the_conversation)

            """ Check conversation threads for replies from team members """
            self._check_conversation_for_replies(
                self.dictionary_of_tag_and_names,
                conv_id,
                product_or_plugin=product_name,
            )

        return {k: dict(v) for k, v in self.dictionary_of_tag_and_names.items()}
