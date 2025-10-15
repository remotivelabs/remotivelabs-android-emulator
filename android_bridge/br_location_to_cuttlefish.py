from remotivelabs.broker import FrameName, SignalValue
import requests
import json


class BrokerToCuttlefish:
    def __init__(
        self,
        cuttlefish_url,
        longitude_signal_name,
        latitude_signal_name,
    ):
        self.cuttlefish_url = cuttlefish_url
        self.longitude_signal_name = longitude_signal_name
        self.latitude_signal_name = latitude_signal_name
        self.lat = None
        self.lon = None

    def redirect_location_signals_to_cuttlefish(
        self, name: FrameName, value: SignalValue
    ):
        if name == self.longitude_signal_name:
            self.lon = float(value)
        if name == self.latitude_signal_name:
            self.lat = float(value)

        if self.lat is not None and self.lon is not None:
            payload = {
                "delay": 0,
                "coordinates": [
                    {
                        "latitude": self.lat,
                        "longitude": self.lon,
                        "elevation": 15,
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
                print("Location sent successfully.")
            except requests.RequestException as e:
                print(f"Failed to send location: {e}")
