from remotivelabs.broker import FrameName, SignalValue

from android_bridge.signal_mapping import SignalMapping

from .libs.adb.adb_emulator import AndroidEmulator
from .libs.vhal import vhal_emulator as vhal_emu


class BrokerToAAOS:
    def __init__(
        self,
        android_emulator: AndroidEmulator,
        signal_mappings: dict[str, SignalMapping],
    ):
        self.vhal = vhal_emu.Vhal(device=android_emulator.emulator_name)
        self.signal_mappings = signal_mappings

    def _set_property(self, property_id, area_id, value):
        """Set a property in AAOS via VHAL"""
        try:
            self.vhal.set_property(property_id, area_id, value)
        except Exception as e:
            print(f"Error setting property ID 0x{property_id:08x}: {e}")
            pass

    def update_property(self, name: FrameName, value: SignalValue):
        mapping = self.signal_mappings.get(name)
        if mapping is not None:
            if mapping.signal == "TRACTION_CONTROL_ACTIVE":
                self._set_property(mapping.property_id, mapping.area_id, bool(value))
                # pass
            else:
                self._set_property(mapping.property_id, mapping.area_id, value)
