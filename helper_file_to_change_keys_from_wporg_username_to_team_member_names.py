import json
def map_wporg_usernames_to_names(result_dict, config_file="config.json"):
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    wporg_mapping = config.get('WP_ORG_USERNAMES', {})
    
    mapped_result = {}
    for wporg_username, count in result_dict.items():
        mapped_name = wporg_mapping.get(wporg_username, wporg_username)
        mapped_result[mapped_name] = count
    
    return mapped_result