from pprint import pprint
from core_system import CoreSystem
import config

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

    def categorize_helpscout_tags(self):
        all_tags = self.retrieve_all_tags()
        
        config_categories = {
            'plugins_tags': config.PLUGINS_TAGS,
            'themes_tags': config.THEMES_TAGS,
        }
        
        results = {
            'plugins_tags': [],
            'themes_tags': [],
            'wordpress_tickets_tags': [config.WORDPRESS_TICKETS_TAGS],
            'payment': [config.PAYMENT]
        }

        def tags_match(helpscout_tag, config_tag):
            hs_tag = helpscout_tag.lower()
            cfg_tag = config_tag.lower()

            if (cfg_tag in hs_tag and hs_tag.startswith(cfg_tag)) or (hs_tag == cfg_tag):
                return True
            
            return None
        
        for hs_tag in all_tags:
            categorized = False
            
            for category, config_tags in config_categories.items():
                for config_tag in config_tags:
                    match_type = tags_match(hs_tag, config_tag)

                    if match_type:
                        results[category].append(hs_tag)
                        categorized = True
                        break
                
                if categorized:
                    break
        
        return results

    def categorize_pro_and_free_versions(self, results):
        new_results = {
            'pro_plugins': [],
            'free_plugins': [],
            'pro_themes': [],
            'free_themes': []
        }

        def category_logic(source_field, object_to_check, target_field):
            for tag in object_to_check.get(source_field, []):
                if contains_pro(tag):
                    new_results['pro_' + target_field].append(tag)
                else:
                    new_results['free_' + target_field].append(tag)

        def contains_pro(tag):
            return 'pro' in tag.lower()
        
        category_logic('plugins_tags', results, 'plugins')
        category_logic('themes_tags', results, 'themes')

        return new_results
    
def main():
    tag_manager = ManageTags(config.CLIENT_ID, config.CLIENT_SECRET)

    results = tag_manager.categorize_helpscout_tags()

    final_results = tag_manager.categorize_pro_and_free_versions(results)
    pprint(final_results)
if __name__ == "__main__":
    main()
