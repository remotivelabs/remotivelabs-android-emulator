from remotivelabs.broker import FrameName, SignalValue

from .libs.adb.adb_emulator import AndroidEmulator


class BrokerToEmulator:
    def __init__(
        self,
        emulator: AndroidEmulator,
        longitude_signal_name: str,
        latitude_signal_name: str,
    ):
        self.emulator = emulator
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
