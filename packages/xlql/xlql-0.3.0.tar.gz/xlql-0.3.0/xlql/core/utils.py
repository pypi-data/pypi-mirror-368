import os
import json
import duckdb
import pandas as pd

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".xlql")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def ensure_config_exists():
    """Create config file if it doesn't exist."""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"base_db_location": ""}, f)

def get_base_db_location():
    ensure_config_exists()
    with open(CONFIG_FILE, "r") as f:
        return json.load(f).get("base_db_location", "")
    
# def get_base_db_location():
#     """
#     Helper function to fetch the base DB location as entered by user
     
#     """
#     with open("config.py", "r") as file:
#         for line in file:
#             if line.startswith("BASE_DB_LOCATION="):
#                 return line.split("=", 1)[1].strip().strip("'\"")
            
# def add_base_db_location(base_db_location):
#     """
#     Helper function to add base DB location to config.py file
#     """
#     with open("config.py", "w") as config_file:
#         config_file.write(f"BASE_DB_LOCATION='{base_db_location}'")
def add_base_db_location(path):
    ensure_config_exists()
    with open(CONFIG_FILE, "r+") as f:
        data = json.load(f)
        data["base_db_location"] = path
        f.seek(0)
        json.dump(data, f)
        f.truncate()
    
def get_csv_path(db_name, table_name):
    """
    Helps locating tables stored as csv files.
    
    :params db_name: name of the DB where table is.
    :params table_name: name of the table.
    :return: Returns path to the csv
    """
    base_path = get_base_db_location()
    return os.path.join(base_path, "databases", db_name, table_name)

def run_query_on_csv(query: str, db_name: str, table_name: str):
    """
    Helper function for show and desc commands.

    :param query: The query user want to execute.
    :param db_name: name of the database where the table is present.
    :param table_name: name of the table on which user want to run the query
    :return: A dataframe containing result from the query
    """
    base_path = get_base_db_location()
    if not base_path:
        raise FileNotFoundError("Base DB location is not set.")

    csv_path = os.path.join(base_path, "databases", db_name, table_name)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Table (CSV) '{table_name}' not found in '{db_name}'.")

    con = duckdb.connect()
    try:
        # Register as a temp view to allow using `table_name` in the query
        con.execute(f"CREATE OR REPLACE VIEW temp_table AS SELECT * FROM read_csv_auto('{csv_path}')")
        
        # Replace any mention of table_name in the query with `temp_table`
        safe_query = query.replace(table_name, "temp_table")
        result = con.execute(safe_query).fetchdf()
        result =result.fillna("")
        result = result.astype(str)
        return result
    finally:
        con.close()

def get_csv_headers(file_path):
    """
    Returns the headers (column names) of a CSV file using pandas.
    
    :param file_path: Path to the CSV file
    :return: List of header names
    """
    try:
        df = pd.read_csv(file_path, nrows=0)  # Read only the headers
        return df.columns.tolist()
    except FileNotFoundError:
        print(f"\033[91m[ERROR]\033[0m File not found: {file_path}")
        return []
    except Exception as e:
        print(f"\033[91m[ERROR]\033[0m Failed to read CSV headers: {e}")
        return []

def read_query_from_file(file_path):
    """
    Reads query from the file provide by user.

    :param file_path: path of the file containing query
    :return: Query written in the file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            query = f.read().strip()
        return query
    except FileNotFoundError:
        print(f"[ERROR] File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None
    
def register_csv(conn, db_folder):
    """
    Registers every CSV in db_folder as a DuckDB table.
    Table names are derived from the CSV filename (without extension).
    """
    base_path = get_base_db_location() + 'databases/' + db_folder
    for file in os.listdir(base_path):
        if file.lower().endswith(".csv"):
            table_name = os.path.splitext(file)[0]
           
            csv_path = os.path.join(base_path, file)
            conn.execute(f"""
                CREATE OR REPLACE VIEW "{table_name}" AS 
                SELECT * FROM read_csv_auto('{csv_path}', header=True)
            """)