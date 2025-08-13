import json
import os
import requests
from castleguard_sdk.castleguard_base import CastleGuardBase


class Translate(CastleGuardBase):

    def _construct_translation_file_name(self, target_document, document):
        base_file_name = document.get('fileName').split(".")[0]

        source_lang = document.get('sourceLanguage')
        target_lang = document.get('targetLanguage')

        file_name = f"{base_file_name}_{source_lang}_to_{target_lang}_{target_document}"

        return self._add_extention_to_translation_file_name(target_document, file_name, document)

    def _add_extention_to_translation_file_name(self, target_document, file_name, document):
        extention = "unknown"
        target_file_extension = document.get('internalTargetFileName').split(".")[-1]
        source_file_extension = document.get('internalSourceFileName').split(".")[-1]
        if target_document == "original":
            extention = source_file_extension

        elif target_document == "translated":
            extention = target_file_extension

        return f"{file_name}.{extention}"

    def _download_translation_document(
        self,
        document_id,
        target_document,
        save_dir=".",
        file_name=None
    ):
        """
        Downloads a translation document.

        :param document_id: The ID of the translation document.
        :param target_document: The target document to download (original or translated).
        :param save_path: Path to save the downloaded document. Default is the current directory.
        :param file_name: Name of the downloaded document. Default is constructed from the document metadata.
        :return: Path to the downloaded document if successful, None otherwise.
        """
        # /api/v1/translation/document/download/{documentId}
        url = f'{self.base_url}/translation/document/download/{document_id}'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        if target_document == "original":
            url += "?translatedDocument=false"
        elif target_document == "translated":
            url += "?translatedDocument=true"
        else:
            self.log(f"Invalid target document: {target_document}", logLevel=3)
            return None

        # get by document id
        get_by_id_url = f'{self.base_url}/translation/document/{document_id}'
        document = requests.get(get_by_id_url, headers=headers)
        if document.status_code != 200:
            self.log(f"Failed to get translation document: {document.text}", logLevel=3)
            return None
        if file_name is None:
            file_name = self._construct_translation_file_name(target_document, document.json())
        else:
            file_name = self._add_extention_to_translation_file_name(
                target_document,
                file_name,
                document.json())
        return self._download_document(url, headers, file_name, save_dir)

    def translate_text(self, text, source_lang='en', target_lang='fr'):
        """
        Translates text from one language to another.

        :param text: The text to translate.
        :param source_lang: Source language code.
        :param target_lang: Target language code.
        :return: Translated text or None if the request fails.
        """
        url = f'{self.base_url}/translation/instant'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        payload = {
            "originalText": text,
            "sourceLanguageCode": source_lang,
            "targetLanguageCode": target_lang
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            translated_text = response.text
            #self.log(f"Translated text: {translated_text}", logLevel=1)
            return translated_text
        else:
            self.log(f"Translation failed: {response.text}", logLevel=3)
            return None

    def translate_texts(self, texts, source_langs, target_langs):
        """
        Translates multiple texts from one language to another.

        :param texts: List of texts to translate.
        :param texts: List of source language codes.
        :param texts: List of target language codes.
        :return: List of translated texts or None if the request fails or input lengths do not match.
        """

        if len(texts) != len(source_langs) or len(texts) != len(target_langs):
            self.log("The number of texts, source languages, and target languages must be the same.", logLevel=3)
            return None

        url = f'{self.base_url}/translation/instant-multiple'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        payload = [
            {
                "originalText": text,
                "sourceLanguageCode": source_lang,
                "targetLanguageCode": target_lang
            } for text, source_lang, target_lang in zip(
                texts, source_langs, target_langs
            )
        ]

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            translated_text = response.text
            return json.loads(translated_text)
        else:
            self.log(f"Translation failed: {response.text}", logLevel=3)
            return None

    def translate_document(self, file_path, source_lang='en', target_lang='fr', keep_original=True):
        """
        Uploads and transcribes a document/file for translation.

        :param file_path: Path to the file to transcribe.
        :param source_lang: Source language code.
        :param target_lang: Target language code.
        :param keep_original: Whether to keep the original document. Default is True.
        :return: Document ID if successful, None otherwise.

        """
        url = f'{self.base_url}/translation/document'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        if file_path.startswith("."):
            file_path = os.path.join(self._get_caller_file_path(), file_path)

        try:
            files = {
                'file': open(file_path, 'rb'),
                'sourceLanguageCode': source_lang,
                'targetLanguageCode': target_lang,
                'keepOriginal': keep_original
            }
        except FileNotFoundError as e:
            self.log(f"File not found: {e}", logLevel=3)
            return None

        response = requests.post(url, headers=headers, files=files)

        if response.status_code != 200:
            self.log(f"Failed to upload file for translation: {response.text}", logLevel=3)            
            return None

        document_id = response.json().get('id')
        status_code = self.get_translation_document_status(document_id)
        if status_code and status_code == "success":
            return document_id
        return None

    def translate_documents(self, file_path_list, source_lang='en', target_lang='fr', keep_original=True):
        """
        Uploads and transcribes a list of documents/files for translation.

        :param file_path_list: List of paths to the files to transcribe.
        :param source_lang: Source language code.
        :param target_lang: Target language code.
        :param keep_original: Whether to keep the original document. Default is True.
        :return: List of document ID and status code pairs if successful, None otherwise.
        """
        url = f'{self.base_url}/translation/documents'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        file_binaries = []
        for file_path in file_path_list:
            if file_path.startswith("."):
                file_path = os.path.join(self._get_caller_file_path(), file_path)
            try:
                file_binaries.append(('files', open(file_path, 'rb')))
            except FileNotFoundError as e:
                self.log(f"f{file_path} not found: {e}", logLevel=3)
                return None

        # Separate non-file data as `data` rather than in `files`
        data = {
            'sourceLanguageCode': source_lang,
            'targetLanguageCode': target_lang,
            'keepOriginal': str(keep_original).lower()  # Convert boolean to lowercase string if needed
        }
        # Make the POST request
        response = requests.post(url, headers=headers, files=file_binaries, data=data)

        # Close file handlers after the request
        for _, file in file_binaries:
            file.close()

        if response.status_code != 200:
            self.log(f"Failed to upload file for translation: {response.text}", logLevel=3)            
            return None

        document_ids = [doc.get('id') for doc in response.json()]
        return self.get_translation_documents_status(document_ids)

    def download_translation_original(self, document_id, save_path=".", file_name=None):
        """

        Downloads the original document of a translation.

        :param document_id: The ID of the translation document.
        :param save_path: Path to save the downloaded document. Default is the current directory.
        :param file_name: Name of the downloaded document. Default is constructed from the document metadata.
        :return: Path to the downloaded document if successful, None otherwise.
        """
        return self._download_translation_document(document_id, "original", save_path, file_name)

    def download_translation_translated(self, document_id, save_path=".", file_name=None):
        """
        Downloads the translated document of a translation.

        :param document_id: The ID of the translation document.
        :param save_path: Path to save the downloaded document. Default is the current directory.
        :param file_name: Name of the downloaded document. Default is constructed from the document metadata.
        """
        return self._download_translation_document(document_id, "translated", save_path, file_name)

    def get_translation_document_status(self, document_id):
        """
        Gets the status of a translation document.

        :param document_id: The ID of the translation document.
        :return: Status code if successful, None otherwise.
        """
        url = f'{self.base_url}/translation/document/{document_id}'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        return self._get_status_code(url, headers, "translation")

    def get_translation_documents_status(self, document_ids):
        """
        Gets the status of multiple translation documents.

        :param document_ids: The IDs of the translation documents.
        :return: List of status codes if successful, None otherwise.

        """
        url = f'{self.base_url}/translation/documents'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        return self._get_status_codes(document_ids, url, headers, "translation")
