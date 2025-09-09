from helper_file_to_export_csvs_to_list import export_csv_to_list
from helper_file_to_make_csv_from_list import make_csv

all_ids = set(export_csv_to_list('CSVs/filtered_optimole_conversations_ids.csv'))
filtered_ids = set(export_csv_to_list('CSVs/filtered_optimole_conversations.csv'))
ids_to_check = all_ids - filtered_ids
make_csv(list(ids_to_check),'CSVs/filtered_optimole_conversations_no_replies.csv')
