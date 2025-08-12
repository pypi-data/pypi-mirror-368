import os
import shutil
import questionary
from xlql.core.utils import get_base_db_location

def main(args):
    db_location = get_base_db_location()

    if not db_location:
        print("\033[2m\033[32mTry running `xlql createdb` to get started.\033[0m")
        return

    if not hasattr(args, 'db_name') or not args.db_name:
        print("\033[91m[ERROR]\033[0m Please specify a database name. Usage: xlql delete {db_name}")
        return

    db_folder = os.path.join(db_location, "databases", args.db_name)

    if not os.path.exists(db_folder):
        print(f"\033[91m[ERROR]\033[0m Database '{args.db_name}' does not exist.")
        return

    # Get list of tables (files or folders inside the database folder)
    tables = os.listdir(db_folder)

    if not tables:
        print("\033[93m[INFO]\033[0m No tables to delete.")
        return

    # Show selection menu
    selected_table = questionary.select(
        "Select the table to delete:",
        choices=tables
    ).ask()

    if selected_table:
        confirm = questionary.confirm(
            f"Are you sure you want to delete '{selected_table}'?"
        ).ask()

        if confirm:
            full_path = os.path.join(db_folder, selected_table)
            # If it's a folder or a file, delete accordingly
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                os.remove(full_path)
            print(f"\033[92m[SUCCESS]\033[0m Table '{selected_table}' deleted.")
        else:
            print("\033[94m[INFO]\033[0m Deletion aborted.")