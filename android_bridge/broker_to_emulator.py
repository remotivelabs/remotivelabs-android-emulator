from remotivelabs.broker import FrameName, SignalValue

from android_bridge.signal_mapping import SignalMapping

from .libs.emulator.adb.adb_emulator import AndroidEmulator
from .libs.emulator.vhal import vhal_emulator


class BrokerToEmulator:
    def __init__(
        self,
        emulator_name: str,
        longitude_signal_name: str,
        latitude_signal_name: str,
        signal_mappings: dict[str, SignalMapping],
    ):
        self.emulator = AndroidEmulator(emulator_name=emulator_name)
        self.vhal = vhal_emulator.Vhal(None)
        self.signal_mappings = signal_mappings
        self.longitude_signal_name = longitude_signal_name
        self.latitude_signal_name = latitude_signal_name
        self.lon = None
        self.lat = None

    def redirect_location_signals_to_emulator(
        self, name: FrameName, value: SignalValue
    ):
        # Extract latitude and longitude from the signals dict
        # Only one is received in each frame so same them between updates
        if name == self.longitude_signal_name:
            self.lon = float(value)
        if name == self.latitude_signal_name:
            self.lat = float(value)

        if self.lat is not None and self.lon is not None:
            self.emulator.send_fix(str(self.lon), str(self.lat))

    def update_property(self, name: FrameName, value: SignalValue):
        mapping = self.signal_mappings.get(name)
        if mapping is not None:
            if mapping.signal == "TRACTION_CONTROL_ACTIVE":
                self._set_property(mapping.property_id, mapping.area_id, bool(value))
            else:
                self._set_property(mapping.property_id, mapping.area_id, value)

    def _set_property(self, property_id, area_id, value):
        """Set a property in AAOS via VHAL"""
        try:
            self.vhal.set_property(property_id, area_id, value)
        except Exception as e:
            print(f"Error setting property ID 0x{property_id:08x}: {e}")
