import os
from xlql.core.utils import get_base_db_location, add_base_db_location
def main(args):
    db_location = get_base_db_location()
    
    if db_location == "" or db_location == None:
        base_db_location = input("Please enter base location to store your db: ")
        db_location = base_db_location
        add_base_db_location(base_db_location)

    db_location = os.path.join(db_location, "databases")
    for item in os.listdir(db_location):
        full_path = os.path.join(db_location ,item)
        if os.path.isdir(full_path):
            print(item)