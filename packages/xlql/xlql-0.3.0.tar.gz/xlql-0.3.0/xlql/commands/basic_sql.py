import os
import duckdb
import questionary
from xlql.core.utils import get_base_db_location, add_base_db_location, get_csv_path, run_query_on_csv, get_csv_headers
from tabulate import tabulate

def get_db_path(db_name):
    base_path = get_base_db_location()
    if not base_path:
        base_path = input("Please enter base location to store your db: ")
        add_base_db_location(base_path)
    return os.path.join(base_path, "databases", db_name)

def list_databases():
    base_path = get_base_db_location()
    if not base_path:
        print("\033[2m\033[32mTry running `xlql createdb` to get started.\033[0m")
        return
    db_root = os.path.join(base_path, "databases")
    if not os.path.exists(db_root):
        return []
    return [folder for folder in os.listdir(db_root) if os.path.exists(os.path.join(db_root, folder))]

def list_tables(db_name):
    db_location = get_base_db_location()
    if not db_location:
        print("\033[2m\033[32mTry running `xlql createdb` to get started.\033[0m")
        return
    
    db_folder = os.path.join(db_location, "databases", db_name)
    if not os.path.exists(db_folder):
        return []
    
    return [f for f in os.listdir(db_folder) if os.path.isfile(os.path.join(db_folder, f))]

def connect_to_db():
    return duckdb.connect(database=':memory:')

def show_table(args=None):
    try:
        db_name = args.db_name if args and args.db_name else questionary.select(
            "Select a database:", choices=list_databases()
        ).ask()
        if not db_name:
            print("[INFO] No database selected.")
            return
        
        tables = list_tables(db_name)
        if not tables:
            print(f"[INFO] The selected database '{db_name}' does not contain any tables (CSV files).")
            print("Please add a file to the database folder before continuing.")
            return
        
        table_name = args.table_name if args and args.table_name else questionary.select(
            "Select a table (CSV file):", choices=tables
        ).ask()
        if not table_name:
            print("[INFO] No table selected.")
            return

        num_rows = int(args.num_rows) if args and args.num_rows else int(
            questionary.text("Enter number of rows to show:").ask()
        )

        csv_path = get_csv_path(db_name, table_name)
        if not os.path.exists(csv_path):
            print(f"[ERROR] Table file '{csv_path}' does not exist.")
            return

        query = f"SELECT * FROM {table_name} LIMIT {num_rows};"
        result = run_query_on_csv(query, db_name, table_name)
        print(tabulate(result, headers=get_csv_headers(csv_path), tablefmt='psql', showindex=False))

    except Exception as e:
        print(f"[ERROR] {str(e)}")

def describe_table(args=None):
    try:
        db_name = args.db_name if args and args.db_name else questionary.select(
            "Select a database:", choices=list_databases()
        ).ask()
        if not db_name:
            print("[INFO] No database selected.")
            return

        table_name = args.table_name if args and args.table_name else questionary.select(
            "Select a table (CSV file):", choices=list_tables(db_name)
        ).ask()
        if not table_name:
            print("[INFO] No table selected.")
            return

        csv_path = get_csv_path(db_name, table_name)
        if not os.path.exists(csv_path):
            print(f"[ERROR] Table file '{csv_path}' does not exist.")
            return

        query = f"DESCRIBE {table_name};"
        result = run_query_on_csv(query, db_name, table_name)
        print(tabulate(result, headers=result.columns.tolist(), tablefmt='psql', showindex=True))

    except Exception as e:
        print(f"[ERROR] {str(e)}")
