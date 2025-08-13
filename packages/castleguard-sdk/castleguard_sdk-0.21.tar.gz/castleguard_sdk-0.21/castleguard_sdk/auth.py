

import requests
from castleguard_sdk.castleguard_base import CastleGuardBase


class Auth(CastleGuardBase):

    def __init__(self, base_url, username, password, default_version="v1"):
        super().__init__(
            base_url, username, password, default_version=default_version
        )

    def authenticate(self):
        """
        Authenticates the user and retrieves the access token.

        :return: Access token or None if authentication fails.
        """
        url = f'{self.base_url}/auth/token'
        payload = {
            "account": self.username,
            "password": self.password
        }

        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                self.token = response.json().get('token')
                if self.token:
                    print("Authentication successful.")
                else:
                    print("Failed to retrieve token from "
                          "authentication response.")
            else:
                print(f"Failed to authenticate: {response.status_code} - "
                      f"{response.text}")
        except requests.RequestException as e:
            print(f"Authentication request failed: {e}")
            self.token = None
