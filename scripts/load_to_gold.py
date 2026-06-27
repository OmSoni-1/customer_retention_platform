import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
import os
from azure.storage.filedatalake import DataLakeServiceClient
from sqlalchemy import engine, create_engine, URL
import urllib
import io

load_dotenv()

STORAGE_ACC_NAME = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
STORAGE_ACC_KEY = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
CONTAINER_NAME = os.getenv('AZURE_CONTAINER_NAME')

SQL_SERVER_NAME = os.getenv('AZURE_SQL_SERVER')
SQL_DATABASE = os.getenv('AZURE_SQL_DATABASE')
SQL_USER = os.getenv('AZURE_SQL_USER')
SQL_PASSWORD = os.getenv('AZURE_SQL_PASSWORD')

### ADLS Gen2 connection

account_url = f"https://{STORAGE_ACC_NAME}.dfs.core.windows.net"
service_client = DataLakeServiceClient(account_url, credential=STORAGE_ACC_KEY)

# Reference to container
file_system_client = service_client.get_file_system_client(file_system=CONTAINER_NAME)

# Reference to silver folder
gold_directory_client = file_system_client.get_directory_client("gold")
silver_directory_client = file_system_client.get_directory_client("silver")

'''

connection_url = URL.create(
    drivername = "mssql+pyodbc",
    username = SQL_USER,
    password = SQL_PASSWORD,
    host = SQL_SERVER_NAME,
    query={
        "driver": DRIVER_NAME,
        "Encrypt": "yes",
        "TrustServerCertificate": "no",
        "Connection Timeout": "30"
    }
)

'''

connection_string = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={SQL_SERVER_NAME};"
    f"DATABASE={SQL_DATABASE};"
    f"UID={SQL_USER};"
    f"PWD={SQL_PASSWORD};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=no;"
    f"Connection Timeout=30;"
)

params = urllib.parse.quote_plus(connection_string)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")


table_names = [
    "customer_churn",
    "telco_master",
    "customer_demographics",
    "customer_location",
    "customer_population",
    "customer_services",
    "customer_status"
]

for table in table_names:
    print(f"Starting migration for table {table}...")
    try:
        file_client = silver_directory_client.get_file_client(f"{table}.csv")

        download = file_client.download_file()
        csv_bytes = download.readall()

        df = pd.read_csv(io.BytesIO(csv_bytes))

        print(f"Loaded {len(df)} rows from {table}.csv. Loading it to Azure SQL...")

        df.to_sql(
            name=table,
            con=engine,
            if_exists="replace",
            index=False,
            chunksize=50,
            method="multi"
        )

        print(f"Successfully migrated {table} with {len(df)} rows!")

    except Exception as e:
        print(f"Error processing table {table}: {str(e)}\n")

        continue
