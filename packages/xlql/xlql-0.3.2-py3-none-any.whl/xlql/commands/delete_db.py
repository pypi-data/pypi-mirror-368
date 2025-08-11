import os
import shutil
import questionary
from xlql.core.utils import get_base_db_location, add_base_db_location

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
        print("[INFO] No databases to delete.")
        return

    # Show selection menu
    selected_db = questionary.select(
        "Select the database to delete:",
        choices=db_folders
    ).ask()

    if selected_db:
        confirm = questionary.confirm(
            f"Are you sure you want to delete '{selected_db}'?"
        ).ask()

        if confirm:
            full_path = os.path.join(databases_path, selected_db)
            shutil.rmtree(full_path)
            print(f"[SUCCESS] Database '{selected_db}' deleted.")
        else:
            print("[INFO] Deletion cancelled.")