from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime
from config_loader import load_config
from helper_file_to_export_csvs_to_list import export_csv_to_list
from Database.database_schema import get_connection
from get_last_month_dates import get_last_month_dates

class ConversationTagBase(ABC):
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.dictionary_of_tag_and_names = {}
        config = load_config()
        self.team_members = list(config.get("TEAM_MEMBERS", {}).values())
        self.core_system_helper = self._get_core_system_helper()
        
        start_str, end_str = get_last_month_dates()
        self.start_date = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
        self.end_date = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")

    def _parse_helpscout_date(self, date_str: str) -> datetime:
        try:
            if date_str.endswith('Z'):
                date_str = date_str[:-1]
            if '.' in date_str:
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
            else:
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))

    @abstractmethod
    def _get_core_system_helper(self):
        """Get the core system helper instance."""
        pass

    @property
    @abstractmethod
    def processed_file_for_tags(self) -> str:
        pass

    def _get_threads(self, conversation_id: str) -> Optional[dict]:
        return self.core_system_helper.make_request(
            f"conversations/{conversation_id}/threads"
        )

    def _check_conversation_for_replies(self, dictionary_of_tags_and_names: dict, conversation_id: str, product_or_plugin: Optional[str] = None) -> None:
        threads = self._get_threads(conversation_id)
        if not threads or "_embedded" not in threads:
            print(f"No threads found for conversation ID {conversation_id}")
            return

        for thread in threads["_embedded"].get("threads", []):
            created_by = thread.get("createdBy", {})
            data_of_creation = thread.get("createdAt", "")
            
            if data_of_creation:
                try:
                    thread_date = self._parse_helpscout_date(data_of_creation)
                    if self.start_date <= thread_date <= self.end_date:
                        if created_by.get("type") == "user" and created_by.get("id", 0) > 1:
                            full_name = f"{created_by.get('first', '')} {created_by.get('last', '')}".strip()
                            if full_name in self.team_members:
                                category = self._get_category(product_or_plugin)
                                if category not in dictionary_of_tags_and_names:
                                    dictionary_of_tags_and_names[category] = {}
                                if full_name not in dictionary_of_tags_and_names[category]:
                                    dictionary_of_tags_and_names[category][full_name] = 1
                                else:
                                    dictionary_of_tags_and_names[category][full_name] += 1
                except Exception as e:
                    print(f"Error parsing date {data_of_creation}: {e}")
                    continue

    @abstractmethod
    def _get_category(self, product_or_plugin: str | None) -> str:
        """Get the category for the conversation. Subclasses implement different logic."""
        pass

    def _validate_tag(self, list_of_tags: list[str]) -> Optional[str]:
        if not list_of_tags:
            return None

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(f"""
            SELECT p.name, t.name as tag_name
            FROM products p
            JOIN tags t ON p.id = t.product_id
            WHERE t.name IN ({','.join('?'* len(list_of_tags))})
        """, list_of_tags)

        results = cursor.fetchall()
        connection.close()

        if results:
            return results[0][0]
        return None

    def _get_conversation_data(self, conversation_id: int) -> Optional[dict]:
        return self.core_system_helper.make_request(f"conversations/{conversation_id}")

    def _get_tags_from_conversation(self, conversation: dict) -> list[str]:
        tags = conversation.get("tags", [])
        return [tag["tag"] for tag in tags if "tag" in tag]

    def categorise_filtered_conversations(self) -> dict:
        filtered_ids = export_csv_to_list(self.processed_file_for_tags)

        for conv_id in filtered_ids:
            conversation_data = self._get_conversation_data(conv_id)
            if not conversation_data:
                print(f"No data found for conversation {conv_id}")
                continue

            tags_of_the_conversation = self._get_tags_from_conversation(conversation_data)
            product_name = self._validate_tag(tags_of_the_conversation)

            if product_name and product_name not in self.dictionary_of_tag_and_names:
                self.dictionary_of_tag_and_names[product_name] = {}

            self._check_conversation_for_replies(
                self.dictionary_of_tag_and_names,
                conv_id,
                product_or_plugin=product_name,
            )

        return self.dictionary_of_tag_and_names
