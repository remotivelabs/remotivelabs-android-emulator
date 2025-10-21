from remotivelabs.broker import FrameName, SignalValue

from .libs.cuttlefish.gnss.gnss_client import GnssClient
from .libs.cuttlefish.vhal.vhal_client import VhalClient
from .signal_mapping import SignalMapping


class BrokerToCuttlefish:
    def __init__(
        self,
        cuttlefish_gnss_url: str,
        cuttlefish_vhal_url: str,
        longitude_signal_name,
        latitude_signal_name,
        signal_mappings: dict[str, SignalMapping],
    ):
        self.gnss = GnssClient(cuttlefish_gnss_url)
        self.vhal = VhalClient(
            cuttlefish_vhal_url=cuttlefish_vhal_url,
            on_vhal_prop_change=self._on_vhal_prop_change,
            property_ids_to_subscribe=[358614275],
        )
        self.signal_mappings = signal_mappings
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
            self.gnss.send_gps_vector(longitude=self.lon, latitude=self.lat)

    def update_property(self, name: FrameName, value: SignalValue):
        """Set a property in AAOS via VHAL"""
        mapping = self.signal_mappings.get(name)
        if mapping is not None:
            try:
                self.vhal.set_property(
                    area_id=mapping.area_id, prop=mapping.property_id, value=value
                )
            except Exception as e:
                print(f"Error setting property ID 0x{mapping.property_id:08x}: {e}")
                pass

    def _on_vhal_prop_change(self, area_id, property_id, value):
        print(f"area_id:{area_id} - property_id:{property_id} - value:{value}")
