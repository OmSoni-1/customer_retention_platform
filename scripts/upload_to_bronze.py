from dotenv import load_dotenv
import os
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

# Reference to bronze folder
bronze_directory_client = file_system_client.get_directory_client("bronze")

# List of all the 7 xlsx files

raw_data_files = [
    "CustomerChurn.xlsx",
    "Telco_customer_churn.xlsx",
    "Telco_customer_churn_demographics.xlsx",
    "Telco_customer_churn_location.xlsx",
    "Telco_customer_churn_population.xlsx",
    "Telco_customer_churn_services.xlsx",
    "Telco_customer_churn_status.xlsx"
]

# For each file in the list

for filename in raw_data_files:
    # Build a local path
    local_path = os.path.join("data", "raw", filename)

    # get a filename for that filename inside bronze
    file_client = bronze_directory_client.get_file_client(filename)

    # check if local file exists before trying to open it
    if os.path.exists(local_path):
        # open local file in binary read mode
        with open(local_path, "rb") as local_file:
            # upload to Data Lake
            file_client.upload_data(local_file, overwrite=True)

        # print success message with file name
        print(f"Success: Uploaded {filename} to the bronze layer.")
    else:
        print(f"Error: local file was not found at {local_path}")


print("All files uploaded to bronze layer")