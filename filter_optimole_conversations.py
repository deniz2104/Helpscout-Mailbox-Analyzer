from typing import Optional, List, Tuple
from core_system import CoreSystem
from conversation_filter_base import ConversationFilterBase
from helper_file_to_export_csvs_to_list import export_csv_to_list
from config_loader import get_helpscout_credentials

class FilterOptimoleConversations(ConversationFilterBase):
    def __init__(self, client_id, client_secret):
        super().__init__(
            ids_file='filtered_optimole_conversations_ids.csv',
            tags_file='filtered_optimole_conversations_tags.csv'
        )
        self.core_system_helper = CoreSystem(client_id, client_secret)

    def get_creation_date(self, conversation_id) -> Optional[str]:
        conversation_data = self.core_system_helper.make_request(f"conversations/{conversation_id}")
        return conversation_data.get('createdAt') if conversation_data else None

    def get_threads(self, conversation_id):
        return self.core_system_helper.make_request(f"conversations/{conversation_id}/threads")

    def filter_conversations(self) -> Tuple[List[str], int]:
        list_of_ids_with_replies = self.has_conversation_replies()
        return list_of_ids_with_replies, len(list_of_ids_with_replies)

    def export_filtered_conversations(self, output_file: str) -> None:
        filtered_ids, _ = self.filter_conversations()
        self.make_csv(filtered_ids, output_file)

    def has_conversation_replies(self) -> List[str]:
        list_of_ids_with_replies = []
        conversation_ids = export_csv_to_list(self.ids_file)
        for conversation_id in conversation_ids:
            threads = self.get_threads(conversation_id)
            if not threads or '_embedded' not in threads:
                print(f"No threads found for conversation ID {conversation_id}")
                continue

            for thread in threads['_embedded']['threads']:
                created_by = thread.get('createdBy', {})
                if created_by.get('type') == 'user' and created_by.get('id', 0) > 1 and (created_by.get('first') != 'Helpscout' and created_by.get('last') != 'Scout'):
                    list_of_ids_with_replies.append(conversation_id)
                    break

        return list_of_ids_with_replies 

def main():
    client_id, client_secret = get_helpscout_credentials()
    filter_optimole = FilterOptimoleConversations(client_id, client_secret)
    filter_optimole.export_filtered_conversations('filtered_optimole_conversations_with_replies.csv')

if __name__ == "__main__":
    main()