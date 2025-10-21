import json

import requests
import urllib3


class GnssClient:
    def __init__(self, cuttlefish_url: str):
        urllib3.disable_warnings()  # Cuttlefish runs the grpc proxy over https using a self-signed certificate
        self.cuttlefish_url = cuttlefish_url

    def send_gps_vector(self, longitude: float, latitude: float, elevation: float = 15):
        payload = {
            "delay": 0,
            "coordinates": [
                {
                    "latitude": latitude,
                    "longitude": longitude,
                    "elevation": elevation,
                }
            ],
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(
                self.cuttlefish_url + "/services/GnssGrpcProxy/SendGpsVector",
                headers=headers,
                data=json.dumps(payload),
                verify=False,  # Only use this in dev/testing
                timeout=10,  # Set a timeout of 10 seconds
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to send location: {e}")
