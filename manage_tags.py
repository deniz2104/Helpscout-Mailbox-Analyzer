from core_system import CoreSystem
import config
from pprint import pprint
class ManageTags:
    def __init__(self,client_id,client_secret):
        self.core_system_helper = CoreSystem(client_id,client_secret)

    def get_all_the_tags_json(self,number_of_page):
        return self.core_system_helper.make_request("tags",params={"page":number_of_page})

    def retrieve_all_tags(self):
        page = 1
        all_pages = self.get_all_the_tags_json(page).get('page', {}).get('totalPages', 1)
        all_tags = []
        while page <= all_pages:
            tags_data = self.get_all_the_tags_json(page).get('_embedded', {}).get('tags', [])
            if not tags_data:
                break
            all_tags.extend(tag.get('name', '') for tag in tags_data)
            page += 1
        return all_tags
