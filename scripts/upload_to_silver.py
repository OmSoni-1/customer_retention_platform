import pandas as pd
from io import StringIO
from dotenv import load_dotenv
import os
from pathlib import Path
from azure.storage.filedatalake import DataLakeServiceClient

load_dotenv()

STORAGE_ACC_NAME = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
STORAGE_ACC_KEY = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
CONTAINER_NAME = os.getenv('AZURE_CONTAINER_NAME')

### ADLS Gen2 connection

account_url = f"https://{STORAGE_ACC_NAME}.dfs.core.windows.net"
service_client = DataLakeServiceClient(account_url, credential=STORAGE_ACC_KEY)

# Reference to container
file_system_client = service_client.get_file_system_client(file_system=CONTAINER_NAME)

# Reference to silver folder
silver_directory_client = file_system_client.get_directory_client("silver")

# Function to standardize the column names and bring them to snake casing
def to_snake_casing(df) -> pd.DataFrame:
    df.columns = (
        df.columns
        .str.lower()
        .str.strip()
        .str.replace(" ", "_", regex=False)
    )

    return df

customer_churn_df = pd.read_excel(Path.cwd().resolve().parent/"data"/"raw"/"CustomerChurn.xlsx")
telco_master_df =  pd.read_excel(Path.cwd().resolve().parent/"data"/"raw"/"Telco_customer_churn.xlsx")
customer_demographics_df =  pd.read_excel(Path.cwd().resolve().parent/"data"/"raw"/"Telco_customer_churn_demographics.xlsx")
customer_location_df = pd.read_excel(Path.cwd().resolve().parent/"data"/"raw"/"Telco_customer_churn_location.xlsx")
customer_population_df =  pd.read_excel(Path.cwd().resolve().parent/"data"/"raw"/"Telco_customer_churn_population.xlsx")
customer_services_df = pd.read_excel(Path.cwd().resolve().parent/"data"/"raw"/"Telco_customer_churn_services.xlsx")
customer_status_df =  pd.read_excel(Path.cwd().resolve().parent/"data"/"raw"/"Telco_customer_churn_status.xlsx")


df_list = [
    customer_churn_df,
    telco_master_df,
    customer_demographics_df,
    customer_location_df,
    customer_population_df,
    customer_services_df,
    customer_status_df
]

for df in df_list:
    to_snake_casing(df)

customer_churn_df['total_charges'] = pd.to_numeric(customer_churn_df['total_charges'], errors='coerce')
telco_master_df['total_charges'] = pd.to_numeric(telco_master_df['total_charges'], errors='coerce')

customer_churn_df["total_charges"] = customer_churn_df["total_charges"].fillna(0)
telco_master_df["total_charges"] = telco_master_df["total_charges"].fillna(0)

customer_services_df["offer"] = customer_services_df["offer"].fillna("No Offer")
customer_services_df["internet_type"] = customer_services_df["internet_type"].fillna("No Internet Service")


df_dict = {
    "customer_churn.csv": customer_churn_df,
    "telco_master.csv": telco_master_df,
    "customer_demographics.csv": customer_demographics_df,
    "customer_location.csv": customer_location_df,
    "customer_population.csv": customer_population_df,
    "customer_services.csv": customer_services_df,
    "customer_status.csv": customer_status_df
}

csvs_dict = {}

for name, df in df_dict.items():
    buffer = StringIO()

    df.to_csv(buffer, index=False)

    csvs_dict[name] = buffer.getvalue()


csv_bytes_dict = {
    name: csv_string.encode("utf-8")
    for name, csv_string in csvs_dict.items()
}

for filename, byte_content in csv_bytes_dict.items():
    
    file_client = silver_directory_client.get_file_client(filename)

    print(f"Uploading {filename} to silver...")

    file_client.create_file()

    file_client.upload_data(byte_content, overwrite=True)

print("All 7 dataframe CSVs uploaded to the silver layer!")