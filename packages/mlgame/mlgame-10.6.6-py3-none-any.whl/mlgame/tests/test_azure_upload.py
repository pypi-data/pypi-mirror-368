from datetime import datetime

from mlgame.utils.azure import upload_data_to_azure_blob, upload_data_to_azure_blob_by_container
from .env import AZURE_CONTAINER_URL, AZURE_BLOB_URL


def test_upload_to_azure_blob():
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    blob_name = f"upload/blob_{current_time}.json"
    data = {"key": "value"}
    upload_data_to_azure_blob_by_container(AZURE_CONTAINER_URL, blob_name, [data])


def test_create_new_file_in_azure_blob():
    file_name = "03.json"
    data = {"key": "value"}
    
    upload_data_to_azure_blob(AZURE_BLOB_URL, file_name, [data])