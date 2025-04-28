import requests
import json
from libs.remotive.subscribe import parsing_to_subscribe, subscribe


class BrokerToRest:
    def __init__(self):
        self.args_url, self.args_api_key, self.rest_url, self.signals = parsing_to_subscribe()
        self.signal_name_latitude = self.signals[0][1]
        self.signal_name_longitude = self.signals[1][1]
        self.lat = None
        self.lon = None

    def send_location_via_rest(self, latitude, longitude, elevation=15.0):
        payload = {
            "delay": 0,
            "coordinates": [
                {
                    "latitude": latitude,
                    "longitude": longitude,
                    "elevation": elevation
                }
            ]
        }
        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                self.rest_url + "/services/GnssGrpcProxy/SendGpsVector",
                headers=headers,
                data=json.dumps(payload),
                verify=False,  # Only use this in dev/testing
                timeout=10  # Set a timeout of 10 seconds
            )
            response.raise_for_status()
            print("Location sent successfully.")
        except requests.RequestException as e:
            print(f"Failed to send location: {e}")

    def redirect_location_to_rest(self, signals):
        for signal in signals:
            print(
                "{} {} {} ".format(
                    signal.id.name, signal.id.namespace.name, signal.double
                )
            )
            if signal.id.name == self.signal_name_latitude:
                self.lat = signal.double
            elif signal.id.name == self.signal_name_longitude:
                self.lon = signal.double

            if self.lat is not None and self.lon is not None:
                self.send_location_via_rest(self.lat, self.lon)

    def update_location(self):
        subscribe(
            self.args_url,
            self.args_api_key,
            self.signals,
            on_subscribe=self.redirect_location_to_rest,
            on_change=False
        )


if __name__ == "__main__":
    broker = BrokerToRest()
    broker.update_location()
