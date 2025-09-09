from Database.database_schema import initialize_database
from Database.database_predefined_values import make_database_predefined_values

def main():
    initialize_database()
    make_database_predefined_values() 

if __name__ == "__main__":
    main()