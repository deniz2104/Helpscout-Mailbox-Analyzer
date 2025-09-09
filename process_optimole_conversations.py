from typing import Optional

from base_wporg_conversations import BaseWporgConversations
from config_loader import get_helpscout_credentials, load_config
from helper_file_to_export_csvs_to_list import export_csv_to_list
from Database.database_schema import get_connection


class ProcessOptimoleConversations(BaseWporgConversations):
    def __init__(self, client_id: str, client_secret: str):
        super().__init__(client_id, client_secret)
        self.dictionary_of_tag_and_names = {}
        config = load_config()
        self.team_members = list(config.get("TEAM_MEMBERS", {}).values())

    @property
    def processed_file(self) -> str:
        return "CSVs/filtered_optimole_conversations_no_replies.csv"

    @property
    def config_usernames_key(self) -> str:
        return "WP_ORG_USERNAMES"

    def _get_threads(self, conversation_id: str) -> Optional[dict]:
        return self.core_system_helper.make_request(
            f"conversations/{conversation_id}/threads"
        )

    def _check_conversation_for_replies(self,dictionary_of_tags_and_names: dict,conversation_id: str,product_or_plugin: Optional[str] = None) -> None:
        threads = self._get_threads(conversation_id)
        if not threads or "_embedded" not in threads:
            print(f"No threads found for conversation ID {conversation_id}")
            return

        for thread in threads["_embedded"].get("threads", []):
            created_by = thread.get("createdBy", {})
            if created_by.get("type") == "user" and created_by.get("id", 0) > 1:
                full_name = f"{created_by.get('first', '')} {created_by.get('last', '')}".strip()
                if full_name in self.team_members:
                    category = product_or_plugin or "General Optimole"
                    dictionary_of_tags_and_names[category][full_name] += 1

    def validate_tag(self, list_of_tags: list[str]) -> Optional[str]:
        if not list_of_tags:
            return None

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
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
        filtered_ids = export_csv_to_list("CSVs/filtered_optimole_conversations.csv")

        _ = self.dictionary_of_tag_and_names["General Optimole"]

        for conv_id in filtered_ids:
            conversation_data = self._get_conversation_data(conv_id)
            if not conversation_data:
                print(f"No data found for conversation {conv_id}")
                continue

            tags_of_the_conversation = self._get_tags_from_conversation(conversation_data)
            product_name = self.validate_tag(tags_of_the_conversation)

            self._check_conversation_for_replies(
                self.dictionary_of_tag_and_names,
                conv_id,
                product_or_plugin=product_name,
            )

        return self.dictionary_of_tag_and_names


def main():
    client_id, client_secret = get_helpscout_credentials()
    processor = ProcessOptimoleConversations(client_id, client_secret)
    categorized_results = processor.categorise_filtered_conversations()
    processor.dict_of_usernames = categorized_results

if __name__ == "__main__":
    main()
