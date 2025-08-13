import requests


from castleguard_sdk.anonymizer import Anonymizer
from castleguard_sdk.auth import Auth
from castleguard_sdk.chat import Chat
from castleguard_sdk.ner import Ner
from castleguard_sdk.transcription import Transcription
from castleguard_sdk.translate import Translate
from castleguard_sdk.collection import Collection
from castleguard_sdk.heartbeat import Heartbeat
from castleguard_sdk.vision import Vision


class CastleGuard(Auth, Chat, Translate, Ner, Transcription, Collection, Anonymizer, Heartbeat, Vision):
    def __init__(self, base_url, username="", password="", api_key=None, default_version="v1", store_in_webside=True):
        """
        Initialize the CastleGuard class with base credentials.

        :param base_url: Base URL for the CastleGuard API.
        :param username: Username for authentication.
        :param password: Password for authentication.
        :param default_version: Default API version to use if not provided in base_url.
        """
        self.base_url = self._normalize_url(base_url, default_version)
        if username == "" and password== "" and api_key==None:
            print("Need to pass parameters username='...' and password='...' or api_key='...' ")
            return
        self.username = username
        self.password = password
        self.token = None

        if api_key is None:
            self.authenticate()
        else:
            self.token = api_key

    def text_extraction(self, raw_text):
        """
        Extracts paragraphs from the provided raw text.

        :param raw_text: The raw text to extract paragraphs from.
        :return: A list of paragraphs or None if the request fails.
        """
        url = f'{self.base_url}/text-extraction'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        payload = {
            "rawText": raw_text
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json().get("paragraphs", [])
            else:
                self.log(f"Text extraction failed: {response.status_code} - {response.text}", logLevel=3)
                return None
        except requests.RequestException as e:
            self.log(f"Text extraction request failed: {e}", logLevel=3)
            return None

    def text_extraction_from_document(self, file_path):
        """
        Extracts text from a binary document file.

        :param file_path: Path to the binary file to extract text from.
        :return: Extracted text or None if the request fails.
        """
        url = f'{self.base_url}/text-extraction/document'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        files = {
            'file': open(file_path, 'rb')
        }

        try:
            response = requests.post(url, headers=headers, files=files)
            if response.status_code == 200:
                return response.json()
            else:
                self.log(f"Text extraction from document failed: {response.status_code} - {response.text}", logLevel=3)
                return None
        except requests.RequestException as e:
            self.log(f"Text extraction from document request failed: {e}", logLevel=3)
            return None
