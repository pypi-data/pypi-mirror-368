import os
from xlql.core.utils import get_base_db_location

def main(args):
    db_location = get_base_db_location()

    if not db_location:
        print("\033[2m\033[32mTry running `xlql createdb` to get started.\033[0m")
        return

    if not hasattr(args, 'db_name') or not args.db_name:
        print("\033[91m[ERROR]\033[0m Please specify a database name. Usage: xlql list {db_name}")
        return

    db_folder = os.path.join(db_location, "databases", args.db_name)

    if not os.path.exists(db_folder):
        print(f"\033[91m[ERROR]\033[0m Database '{args.db_name}' does not exist.")
        return

    print(f"\033[94mTables inside database '{args.db_name}':\033[0m")

    files = os.listdir(db_folder)
    if not files:
        print("\033[2mNo tables found in this database.\033[0m")
    else:
        for file in files:
            print(f"  - {file}")
