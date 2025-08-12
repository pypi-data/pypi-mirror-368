import urllib3.util
from azure.storage.blob import ContainerClient, BlobClient
from loguru import logger


import json



def upload_data_to_azure_blob(az_path_blob_url: str, file_name: str, data: list) -> bool:
    """
    Uploads a dictionary to Azure Blob Storage.

    :param az_path_blob_url: The URL of the Azure container.
    :param file_name: The name of the blob to create.
    :param data: The dictionary to upload.
    :return: True if upload is successful, False otherwise.
    """
    # Create a ContainerClient
    path_blob_url = urllib3.util.parse_url(az_path_blob_url)
    file_blob_url = str(path_blob_url).replace(path_blob_url.path, path_blob_url.path+ "/" + file_name)

    # Create a blob client
    blob_client = BlobClient.from_blob_url(file_blob_url)

    # Convert the dictionary to a JSON string
    json_data = json.dumps(data)

    # Upload the JSON string to the blob
    blob_client.upload_blob(json_data, overwrite=True)




def upload_data_to_azure_blob_by_container(az_container_url: str, blob_name: str, data: list) -> bool:
    """
    Uploads a dictionary to Azure Blob Storage.

    :param az_container_url: The URL of the Azure container.
    :param blob_name: The name of the blob to create.
    :param data: The dictionary to upload.
    :return: True if upload is successful, False otherwise.
    """
    try:
        # Create a ContainerClient
        container_client = ContainerClient.from_container_url(az_container_url)

        # Create a blob client
        blob_client = container_client.get_blob_client(blob_name)

        # Convert the dictionary to a JSON string
        json_data = json.dumps(data)

        # Upload the JSON string to the blob
        blob_client.upload_blob(json_data, overwrite=True)



    except Exception as e:
        logger.exception(e)