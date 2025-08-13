
import os
import requests
from castleguard_sdk.castleguard_base import CastleGuardBase


class Transcription(CastleGuardBase):

    def _construct_transcription_file_name(self, target_document, document):
        base_file_name = document.get('fileName').split(".")[0]
        file_name = f"{base_file_name}_{target_document}"
        return self._add_extention_to_transcription_file_name(target_document, file_name, document)

    def _add_extention_to_transcription_file_name(self, target_document, file_name, document):
        extention = "unknown"
        if target_document == "original":
            extention = document.get('internalSourceFileName').split(".")[-1]
        elif target_document == "transcript":
            extention = "txt"
        elif target_document == "srt":
            extention = "srt"
        else:
            self.log(f"Invalid target document: {target_document}", logLevel=3)
            return None

        return f"{file_name}.{extention}"

    def _download_transcription_document(
        self,
        document_id,
        target_document,
        save_path=".",
        file_name=None
    ):

        url = f'{self.base_url}/transcription/document/download/{document_id}'

        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        if target_document == "original":
            url += "?downloadDocumentOptions=0"
        elif target_document == "transcript":
            url += "?downloadDocumentOptions=1"
        elif target_document == "srt":
            url += "?downloadDocumentOptions=2"
        else:
            self.log(f"Invalid target document: {target_document}", logLevel=3)
            return None

        # get by document id
        get_by_id_url = f'{self.base_url}/transcription/document/{document_id}'
        document = requests.get(get_by_id_url, headers=headers)

        if document.status_code != 200:
            self.log(f"Failed to get transcription document: {document.text}", logLevel=3)
            return None
        if file_name is None:
            file_name = self._construct_transcription_file_name(
                target_document,
                document.json()
            )
        else:
            file_name = self._add_extention_to_transcription_file_name(
                target_document,
                file_name,
                document.json()
            )

        return self._download_document(url, headers, file_name, save_path)

    def transcribe(self, file_path, diarization_config=1):
        """
        Uploads and transcribes an audio/file file.
        file path can be relative or absolute path
        relative starts from the 

        :param file_path: Path to the file to transcribe.
        :param diarization_config: Diarization configuration. Default is 1.
        :return: Document ID if successful, None otherwise.
        """
        url = f'{self.base_url}/transcription/document'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        if file_path.startswith("."):
            file_path = os.path.join(self._get_caller_file_path(), file_path)
        files = {}
        try:
            files = {
                'file': open(file_path, 'rb'),
                'taskType': 2,
                'diarizationConfig': diarization_config
            }
        except FileNotFoundError as e:
            self.log(f"f{file_path} not found: {e}", logLevel=3)
            return None

        response = requests.post(url, headers=headers, files=files)
        if response.status_code != 200:
            self.log(f"Failed to upload file for transcription: {response.text}", logLevel=3)            
            return None
        document_id = response.json().get('id')
        status_code = self.get_transcription_document_status(document_id, sync=False)
        if status_code and status_code == "success":
            return document_id
        return None

    def transcribe_multiple(
        self,
        file_path_list,
        diarization_config=1
    ):
        """
        Uploads and transcribes a list of audio files.

        :param file_path_list: List of paths to the files to transcribe.
        :param diarization_config: Diarization configuration. Default is 1.
        :return: List of document ID and status code pairs if successful, None otherwise.
        """
        url = f'{self.base_url}/transcription/document'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'accept': 'text/plain',
        }

        file_path_list = [os.path.join(self._get_caller_file_path(3), file_path) if file_path.startswith(".") else file_path for file_path in file_path_list]

        # Prepare files for the multipart/form-data request
        files = []
        for file_path in file_path_list:
            if file_path.startswith("."):
                file_path = os.path.join(self._get_caller_file_path(), file_path)
            try:
                files.append(open(file_path, 'rb'))
            except FileNotFoundError as e:
                self.log(f"f{file_path} not found: {e}", logLevel=3)
                return None

        try:
            document_ids = []
            # Make the POST request with files and data
            for file in files:
                request_file = {
                    'file': file,
                    'taskType': 2,
                    'diarizationConfig': diarization_config
                }
                response = requests.post(url, headers=headers, files=request_file)

                if response.status_code != 200:
                    # self.log(f"Failed to upload file for transcription: {response.text}", logLevel=3)
                    # return None
                    continue

                document_id = response.json().get('id')
                if document_id:
                    document_ids.append(document_id)
            return self.get_transcription_documents_status(document_ids, sync=False)
        except requests.RequestException as e:
            self.log(f"Transcription request failed: {e}", logLevel=3)
            return None
        finally:
            # Close each file after the request to free resources
            for file_obj in files:
                file_obj.close()

    def get_transcription_document_status(self, document_id, sync=True):
        """
        Gets the status of a transcription document.

        :param document_id: The ID of the transcription document.
        :return: Status code if successful, None otherwise.
        """
        url = f'{self.base_url}/transcription/document/{document_id}'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        if sync:
            return self._get_status_code(url, headers, "transcription")
        else:
            return self._run_coro_sync(
                self._get_status_code_async(url, headers, "transcription")
            )

    def get_transcription_documents_status(self, document_ids, sync=True):
        """
        Gets the status of a transcription document.

        :param document_id: The ID of the transcription document.
        :return: Status code if successful, None otherwise.
        """
        url = f'{self.base_url}/transcription/documents'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        if sync:
            return self._get_status_codes(document_ids, url, headers, "transcription")
        else:
            return self._run_coro_sync(
                self._get_status_codes_async(document_ids, url, headers, "transcription")
            )

    def download_transcription_original_file(self, document_id, save_path=".", file_name=None):
        """
        Downloads the original transcription from a transcription document.

        :param document_id: The ID of the transcription document.
        :param save_path: Path to save the downloaded document. Default is the current directory.
        :param file_name: Name of the downloaded document. Default is constructed from the document metadata.
        :return: saved file path if successful, None otherwise.
        """
        return self._download_transcription_document(document_id, "original", save_path, file_name)

    def download_srt_file(self, document_id,  save_path=".", file_name=None):
        """
        Downloads the SRT file from a transcription document.

        :param document_id: The ID of the transcription document.
        :param save_path: Path to save the downloaded document. Default is the current directory.
        :param file_name: Name of the downloaded document. Default is constructed from the document metadata.
        :return: saved file path if successful, None otherwise.
        """
        return self._download_transcription_document(document_id, "srt", save_path, file_name)

    def download_srt(self, document_id):
        """
        Downloads the SRT file from a transcription document.
        
        :param document_id: The ID of the transcription document.
        :return: SRT text if successful, None otherwise.
        """
        # TODO: update url here if this function remains
        url = f'{self.base_url}/transcription/document/download/{document_id}?downloadDocumentOptions=SRT'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            srt_text = response.text
            #self.log(f"SRT downloaded successfully.", logLevel=1)
            return srt_text
        else:
            self.log(f"Failed to download SRT: {response.text}", logLevel=3)            
            return None
    
    def download_transcription_file(self, document_id,  save_path=".", file_name=None):
        """
        Downloads the transcription from a transcription document.
        :param document_id: The ID of the transcription document.
        :param save_path: Path to save the downloaded document. Default is the current directory.
        :param file_name: Name of the downloaded document. Default is constructed from the document metadata.
        :return: saved file path if successful, None otherwise.
        """
        return self._download_transcription_document(document_id, "transcript", save_path, file_name)
