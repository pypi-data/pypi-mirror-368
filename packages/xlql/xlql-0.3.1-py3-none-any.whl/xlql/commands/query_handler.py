from xlql.core.utils import read_query_from_file, register_csv
import os
import duckdb as dd
from tabulate import tabulate
import uuid

def main(args):
    try:
        db_name = args.db_name
        query_path = args.query_path
        export_format = getattr(args, "format", None)  # csv, parquet, json
        export_path = getattr(args, "output", None)    # file path to save ouput

        # validating db name
        if not db_name:
            print("[ERROR] Database name is required.")
            return

        # validating query path
        if not query_path or not os.path.exists(query_path):
            print(f"[ERROR] Query file '{query_path}' not found.")
            return

        # reading SQL query
        query = read_query_from_file(query_path)
        query = query.removesuffix(';')
        if not query:
            print("[ERROR] Query file is empty.")
            return
        
        # Run query in DuckDB
        conn = dd.connect(':memory:')
        register_csv(conn, db_name)

        if export_format and export_path:
            # If export_path is a directory, generate a filename
            if os.path.isdir(export_path):
                file_ext = export_format.lower()
                file_name = f"xlql_export_{uuid.uuid4().hex[:8]}.{file_ext}"
                export_path = os.path.join(export_path, file_name)

            # Ensure parent directory exists
            os.makedirs(os.path.dirname(export_path), exist_ok=True)

            # Run export
            conn.execute(f"COPY ({query}) TO '{export_path}' (FORMAT {export_format.upper()});")
            print(f"[SUCCESS] Query results exported to '{export_path}' in {export_format.upper()} format.")
        else:
            # Fetch results to Pandas for pretty printing
            result = conn.execute(query).fetchdf()
            if result is not None and not result.empty:
                print(tabulate(result, headers=result.columns, tablefmt="fancy_grid", showindex=False))
            else:
                print("[INFO] Query executed successfully, but returned no results.")

    except Exception as e:
        print(f"[ERROR] {e}")
