
import requests
from castleguard_sdk.castleguard_base import CastleGuardBase


class Heartbeat(CastleGuardBase):

    def heartbeat(self):
        """
        Fetches the health status of various system components.

        :return: A dictionary with the status of each component or None if the request fails.
        """
        url = f'{self.base_url}/heartbeat'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                self.log(f"Failed to get heartbeat: {response.status_code} - {response.text}", logLevel=3)
                return None
        except requests.RequestException as e:
            self.log(f"Heartbeat request failed: {e}", logLevel=3)
            return None

    def healthcheck(self):
        """
        Fetches the health status of the system.

        :return: True if the system is healthy, False otherwise.
        """
        url = f'{self.base_url}/heartbeat'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                self.log(f"Failed to get healthcheck: {response.status_code} - {response.text}", logLevel=3)
                return None

            healths = response.json()
            health_list = []
            for resource_name, health_info in healths.items():
                health_list.append((resource_name, health_info['status']))

            return health_list

        except requests.RequestException as e:
            self.log(f"Healthcheck request failed: {e}", logLevel=3)
            return False
