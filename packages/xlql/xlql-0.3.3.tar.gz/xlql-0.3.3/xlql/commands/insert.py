import os
from xlql.core.utils import get_base_db_location, add_base_db_location
import questionary
import shutil

def main(args):
    db_location = get_base_db_location()

    if not db_location:
        base_db_location = input("Please enter base location to store your db: ")
        db_location = base_db_location
        add_base_db_location(base_db_location)

    databases_path = os.path.join(db_location, "databases")
    
    if not os.path.exists(databases_path):
        print("[ERROR] 'databases' folder does not exist.")
        return

    db_folders = [folder for folder in os.listdir(databases_path)
                  if os.path.isdir(os.path.join(databases_path, folder))]

    if not db_folders:
        print("[INFO] No databases to choose.")
        return

    # Show selection menu
    selected_db = questionary.select(
        "Select the database to use:",
        choices=db_folders
    ).ask()  

    if selected_db:
        confirm = questionary.confirm(
            f"Use '{selected_db}'?"
        ).ask()

    table_name = input("Please enter the table name: ") + '.csv'
    
    if confirm:
        full_path = os.path.join(databases_path, selected_db)
        file_path = input('Enter the absolute path of your file(CSV): ')
        destination_path = os.path.join(full_path, table_name)
        shutil.copy(file_path, destination_path)
        print(f"[SUCCESS] Your file is now added to '{selected_db}'.")
    else:
        print("[INFO] Insertion aborted.")