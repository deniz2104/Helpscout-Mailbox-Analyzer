from typing import List
import concurrent.futures
from core_system import CoreSystem
from helper_file_to_export_csvs_to_list import export_csv_to_list
from helper_file_to_make_csv_from_list import make_csv
from config_loader import get_helpscout_credentials, load_config

class FilterOptimoleConversations:
    def __init__(self, client_id, client_secret):
        self.ids_file = 'CSVs/filtered_optimole_conversations_ids.csv'
        self.core_system_helper = CoreSystem(client_id, client_secret)
        config = load_config()
        self.team_members = list(config.get("TEAM_MEMBERS", {}).values())
        self.max_workers = 10

    def _get_threads(self, conversation_id):
        return self.core_system_helper.make_request(f"conversations/{conversation_id}/threads")

    def _check_conversation_for_replies(self, conversation_id):
        threads = self._get_threads(conversation_id)
        if not threads or '_embedded' not in threads:
            print(f"No threads found for conversation ID {conversation_id}")
            return None

        for thread in threads['_embedded']['threads']:
            created_by = thread.get('createdBy', {})
            full_name = created_by.get('first') + ' ' + created_by.get('last')
            if created_by.get('type') == 'user' and created_by.get('id', 0) > 1 and full_name in self.team_members:
                return conversation_id
        return None

    def has_conversation_replies(self) -> List[str]:
        conversation_ids = export_csv_to_list(self.ids_file)
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = executor.map(self._check_conversation_for_replies, conversation_ids)

        return [result for result in results if result is not None]

def main():
    client_id, client_secret = get_helpscout_credentials()
    filter_optimole = FilterOptimoleConversations(client_id, client_secret)
    filtered_ids = filter_optimole.has_conversation_replies()
    if filtered_ids:
        make_csv(filtered_ids, 'CSVs/filtered_optimole_conversations.csv')
    else:
        print("No conversations found with replies. Creating empty output file.")
        make_csv([], 'CSVs/filtered_optimole_conversations.csv')

if __name__ == "__main__":
    main()