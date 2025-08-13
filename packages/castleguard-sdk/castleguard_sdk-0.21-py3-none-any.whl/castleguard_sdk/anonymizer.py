
import os
import requests
from castleguard_sdk.castleguard_base import CastleGuardBase
from enum import Enum


class Anonymizer(CastleGuardBase):

    def _construct_anonymized_file_name(self, document, anonymized_document):
        base_file_name = document.get('fileName').split(".")[0]
        extention = document.get('internalSourceFileName').split(".")[-1]
        type_of_document = "anonymized" if anonymized_document else "original"
        return f"{base_file_name}_{type_of_document}.{extention}"

    def _add_extention_to_anonymized_file_name(self, file_name, document):
        extention = document.get('internalSourceFileName').split(".")[-1]
        return f"{file_name}.{extention}"

    def _download_anonymized(
        self,
        document_id,
        anonymized_document,
        save_path,
        file_name
    ):

        url = f'{self.base_url}/anonymizer/document/download/{document_id}'
        url += f"?anonymizedDocument={anonymized_document}"
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        # get by document id
        get_by_id_url = f'{self.base_url}/anonymizer/document/{document_id}'
        document = requests.get(get_by_id_url, headers=headers)

        if document.status_code != 200:
            self.log(f"Anonymization request failed: {document.text}", logLevel=3)
            return None

        if file_name is None:
            file_name = self._construct_anonymized_file_name(
                document.json(),
                anonymized_document
            )
        else:
            file_name = self._add_extention_to_anonymized_file_name(
                file_name,
                document.json()
            )

        return self._download_document(url, headers, file_name, save_path, "anonymization")

    def anonymize_document(self, file_path, options=[], regex=""):
        """
        Anonymizes the provided file.

        :param file_path: Path to the file to anonymize.
        :param options: List of EntityType values to anonymize.
        :param regex: Regular expression to anonymize.
        :return: Anonymized text or None if the request fails.
        """
        url = f'{self.base_url}/anonymizer/document'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        if file_path.startswith("."):
            file_path = os.path.join(self._get_caller_file_path(), file_path)
        files = {}
        try:
            files = {
                'file': open(file_path, 'rb')
            }
        except FileNotFoundError as e:
            self.log(f"f{file_path} not found: {e}", logLevel=3)
            return None
        try:
            response = requests.post(url, headers=headers, files=files, data={"nerOptions": options, "regexp": regex})
            if response.status_code != 200:
                self.log(f"Anonymization request failed: {response.text}", logLevel=3)
                return None
            document = response.json()
            return document.get('id', None)
        except requests.RequestException as e:
            self.log(f"Anonymization request failed: {e}", logLevel=3)
            return None

    def anonymize_documents(self, file_paths, options=[], regex=""):
        """
        Anonymizes the provided files.

        :param file_paths: Paths to the files to anonymize.
        :param options: List of EntityType values to anonymize.
        :param regex: Regular expression to anonymize.
        :return: Anonymized text or None if the request fails.
        """
        url = f'{self.base_url}/anonymizer/documents'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        files = []
        for file_path in file_paths:
            if file_path.startswith("."):
                file_path = os.path.join(self._get_caller_file_path(), file_path)
            try:
                files.append(('files', open(file_path, 'rb')))
            except FileNotFoundError as e:
                self.log(f"f{file_path} not found: {e}", logLevel=3)
                return None
        try:
            response = requests.post(url, headers=headers, files=files, data={"nerOptions": options, "regexp": regex})
            if response.status_code != 200:
                self.log(f"Anomyzation request failed: {response.text}", logLevel=3)
                return None
            document_ids = [item.get('id') for item in response.json()]
            return self.get_anonymized_documents_status(document_ids)
        except requests.RequestException as e:
            self.log(f"Anonymization request failed: {e}", logLevel=3)
            return None

    def get_anonymized_document_status(self, document_id):
        """
        Gets the status of a document.

        :param document_id: The ID of the document.
        :return: Status code if successful, None otherwise.
        """
        url = f'{self.base_url}/anonymizer/document/{document_id}'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        return self._get_status_code(url, headers, "anonymization")

    def get_anonymized_documents_status(self, document_ids):
        """
        Gets the status of a document.

        :param document_id: The ID of the document.
        :return: Status code if successful, None otherwise.
        """
        url = f'{self.base_url}/anonymizer/documents'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        return self._get_status_codes(document_ids, url, headers, "anonymization")

    def download_anonymized_original_documnet(self, document_id, save_path=".", file_name=None):
        """
        Downloads the original document from a document.

        :param document_id: The ID of the document.
        :return: Original document text if successful, None otherwise.
        """
        return self._download_anonymized(document_id, False, save_path, file_name)

    def download_anonymized_documnet(self, document_id, save_path=".", file_name=None):
        """
        Downloads the anonymized document from a document.

        :param document_id: The ID of the document.
        :return: anonymized document text if successful, None otherwise.
        """
        return self._download_anonymized(document_id, True, save_path, file_name)


class EntityType(Enum):
    ADDRESS = "ADDRESS"
    CARDINAL = "CARDINAL"
    COMPANY = "COMPANY"
    CRYPTO = "CRYPTO"
    DATE = "DATE"
    DNS = "DNS"
    EMAIL = "EMAIL"
    EVENT = "EVENT"
    FAC = "FAC"
    GPE = "GPE"
    IP = "IP"
    LANGUAGE = "LANGUAGE"
    LAW = "LAW"
    LOC = "LOC"
    MONEY = "MONEY"
    NORP = "NORP"
    ORDINAL = "ORDINAL"
    ORG = "ORG"
    PERCENT = "PERCENT"
    PERSON = "PERSON"
    PHONE = "PHONE"
    PRODUCT = "PRODUCT"
    QUANTITY = "QUANTITY"
    TIME = "TIME"
    WORK_OF_ART = "WORK_OF_ART"
