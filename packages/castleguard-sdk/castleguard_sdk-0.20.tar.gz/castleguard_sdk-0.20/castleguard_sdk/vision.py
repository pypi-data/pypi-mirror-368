

import requests
from castleguard_sdk.castleguard_base import CastleGuardBase


class Vision(CastleGuardBase):

    def vision(self, prompt, file_path):
        """
        Sends a request to the vision endpoint for image-related tasks.

        :param prompt: A descriptive prompt for the vision model, sent as a parameter.
        :param file_path: Path to the image file to send in the request body.
        :return: Response from the vision model or None if the request fails.
        """
        url = f'{self.base_url}/triton/vision'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        files = {
            'file': open(file_path, 'rb')
        }

        # Include the prompt as a parameter in the URL
        params = {
            'prompt': prompt
        }

        try:
            response = requests.post(url, headers=headers, params=params, files=files)
            if response.status_code == 200:
                vision_result = response.text
                return vision_result
            else:
                self.log(f"Vision request failed: {response.status_code} - {response.text}", logLevel=3)
                return None
        except requests.RequestException as e:
            self.log(f"Vision request failed: {e}", logLevel=3)
            return None
