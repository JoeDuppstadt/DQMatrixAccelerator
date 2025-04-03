import os
import sys
import time
import tdclient
from pathlib import Path
import pandas as pd
import requests
from dotenv import load_dotenv

# Configuration - Replace these with your actual values
load_dotenv()
SOURCE_API_KEY = os.getenv("SOURCE_API_KEY") # Your source environment master api key
TARGET_API_KEY = os.getenv("TARGET_API_KEY") # Your target environment master api key
SOURCE_DB = "raw_raymond_james" # Your source database
SOURCE_TABLE = ["rjfs_account_asset",
                "rjfs_account_customer"
                ]
TARGET_DB = "dev_src" # Your target database
API_BASE_URL = "https://api.treasuredata.com"  # Adjust to your region if needed (e.g., api.us.treasuredata.com)
STAGING_LOCATION = f"C:/Users/JoeDuppstadt/Downloads/" # Used to hold the csv file between download and upload

def run_query(client, database, query, engine="hive"):  # Default to Hive since it’s being used
    print(f"Executing query with {engine} engine: {query}")
    try:
        job = client.query(database, query, engine=engine)
        job.wait()
        if job.status() != "success":
            error_msg = job.error() or "No detailed error message"
            debug_info = job.debug.get('stderr', 'No debug info') if hasattr(job, 'debug') else "No debug info"
            raise Exception(f"Query failed\nStatus: {job.status()}\nError: {error_msg}\nDebug: {debug_info}")
        print(f"Query succeeded with Job ID: {job.job_id}")
        return job
    except Exception as e:
        print(f"Query execution error: {e}", file=sys.stderr)
        raise


def create_table_if_not_exists(client, target_db, target_table, schema):
    try:
        print(f"Checking if table {target_table} exists in database {target_db}...")
        client.table(target_db, target_table)
        print(f"Table {target_table} already exists in {target_db}.")
        return False
    except tdclient.api.NotFoundError:
        print(f"Table {target_table} not found in {target_db}. Creating it via REST API...")
        # Convert schema to TD REST API format
        columns = [{"name": col[0], "type": "string" if col[1].lower() == "string" else col[1]} for col in schema]
        payload = {
            "schema": columns  # Explicitly set schema
        }
        headers = {
            "Authorization": f"TD1 {TARGET_API_KEY}",
            "Content-Type": "application/json"
        }
        url = f"{API_BASE_URL}/v3/table/create/{target_db}/{target_table}/log"
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200 and response.status_code != 201:
            raise Exception(f"Failed to create table via REST API: {response.status_code} - {response.text}")
        print(f"Created table {target_table} in {target_db} via REST API with schema: {columns}")
        return True

def export_query_to_csv(client, database, table, output_file):
    # Get table schema to fetch column names
    print(f"Fetching schema for table {table} in database {database}...")
    table_obj = client.table(database, table)
    schema = table_obj.schema

    if isinstance(schema, list) and schema and isinstance(schema[0], list):
        column_names = [col[0] for col in schema]
    elif isinstance(schema, list) and schema and isinstance(schema[0], str):
        column_names = schema
    elif isinstance(schema, list) and schema and hasattr(schema[0], 'name'):
        column_names = [col.name for col in schema]
    else:
        raise Exception(f"Unexpected schema format: {schema}")
    column_names.append('time')

    # Define the query (no 'time' column added here unless in schema)
    query = f"SELECT * FROM {table} limit 2000000"
    print(f"Export query: {query}")

    job = client.query(q=query, db_name=database, engine="hive")  # Use Hive
    job.wait()

    result_data = list(job.result())

    if not result_data:
        print("No data returned from query.")
        return

    # Use column_names directly without appending 'time' unless it’s in the query
    df = pd.DataFrame(result_data, columns=column_names)

    # Save to CSV
    df.to_csv(output_file, index=False)

    return schema


def main():
    SOURCE_TABLE = ["rjfs_account_asset",
                    "rjfs_account_customer"
                    ]

    for table in SOURCE_TABLE:
        TARGET_TABLE = table
        EXPORT_FILE = Path(STAGING_LOCATION + "td_export_" + str(int(time.time())) + ".csv")
        export_file_path = EXPORT_FILE
        try:
            source_client = tdclient.Client(apikey=SOURCE_API_KEY)
            target_client = tdclient.Client(apikey=TARGET_API_KEY)

            schema = export_query_to_csv(source_client, SOURCE_DB, table, export_file_path)
            if not export_file_path.exists():
                raise Exception(f"Export file {export_file_path} was not created.")

            create_table_if_not_exists(target_client, TARGET_DB, TARGET_TABLE, schema)

            target_client.import_file(TARGET_DB, TARGET_TABLE, "csv", str(export_file_path))
            print(f"Imported data to {TARGET_DB}.{TARGET_TABLE}")
            os.remove(EXPORT_FILE)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            if export_file_path.exists():
                print(f"Preserving {export_file_path} for debugging.", file=sys.stderr)
            sys.exit(1)
        print(f"Migration for {table} completed successfully")


if __name__ == "__main__":
    main()