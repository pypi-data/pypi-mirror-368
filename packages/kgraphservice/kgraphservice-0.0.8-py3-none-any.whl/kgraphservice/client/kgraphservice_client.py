import requests
import json


class KGraphServiceClient:

    def __init__(self, host, port, ssl: bool = False):
        self._host = host
        self._port = port
        self._ssl = ssl

    def post(self, request_dict):

        try:
            headers = {'Content-Type': 'application/json'}

            protocol = 'https' if self._ssl else 'http'

            url = f"{protocol}://{self._host}:{self._port}/kgraphservice"

            response = requests.post(url, headers=headers, data=json.dumps(request_dict))

            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None
