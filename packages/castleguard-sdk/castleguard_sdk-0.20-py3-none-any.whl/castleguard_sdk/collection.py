
import os
import time
import requests
from castleguard_sdk.castleguard_base import CastleGuardBase


class Collection(CastleGuardBase):

    def create_collection(self, name, description):
        """
        Creates a new collection.

        :param name: Collection name.
        :param description: Collection description.
        :return: Collection ID if successful, None otherwise.
        """
        url = f'{self.base_url}/collections/collection'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        params = {
            "displayName": name,
            "description": description
        }

        response = requests.post(url, headers=headers, params=params)
        if response.status_code == 200:
            collection_id = response.json().get('id')
            return collection_id
        else:
            self.log(
                f"Failed to create collection: {response.text}", logLevel=3
            )
            return None

    def upload_to_collection(self, collection_id, file_path):
        """
        Uploads a file to a collection.

        :param collection_id: The ID of the collection.
        :param file_path: Path to the file to upload.
        :return: True if successful, False otherwise.
        """
        url = f'{self.base_url}/collections/collection/document/{collection_id}'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        if file_path.startswith('.'):
            file_path = os.path.join(self._get_caller_file_path, file_path)
        files = {}
        try:
            files = {
                'file': open(file_path, 'rb')
            }
        except FileNotFoundError as e:
            self.log(f"{file_path} not found: {e}", logLevel=3)
            return False

        response = requests.post(url, headers=headers, files=files)
        if response.status_code == 200:
            document_id = response.json().get('id')
            if document_id:
                status_code = self.get_collection_document_status_code(
                                collection_id, document_id
                            )
                if status_code and status_code.lower() == "success":
                    return True
        else:
            self.log(
                f"Failed to upload file to collection: {response.text}",
                logLevel=3
            )
        return False

    def get_collection_document_status_code(self, collection_id, document_id, interval=5):
        """
        Gets the status of a document in a collection.

        :param collection_id: The ID of the collection.
        :param document_id: The ID of the document.
        :return: Status code if successful, None otherwise.
        """
        url = f'{self.base_url}/collections/collection/documents/{collection_id}'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        status = None
        while status != 2:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                self.log(f"Failed to get collection document status: {response.text}", logLevel=3)
                return None
            documents = response.json()
            for document in documents:
                if document.get('id') == document_id:
                    job_detail = document.get('jobDetail', {})
                    status = job_detail.get('status', None)
                    if status == 2:
                        status_code = job_detail.get('statusCode', None)
                        return status_code

            time.sleep(interval)
