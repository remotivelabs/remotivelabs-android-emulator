import libs.adb.device as adb
from libs.remotive.subscribe import parsing_to_subscribe, subscribe


class brokerToEmu:
    def __init__(self, adb_dev):
        # Get emulator via adb only once
        self.adb_dev = adb_dev
        self.args_url, self.args_api_key, _cvd, self.signals = parsing_to_subscribe()
        self.signal_name_latitude = self.signals[0][1]
        self.signal_name_longitude = self.signals[1][1]
        self.lon = None
        self.lat = None

    def redirect_location_to_emulator(self, signals):
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
                self.adb_dev.root()
                self.adb_dev.send_fix(str(self.lon), str(self.lat))

    def update_emu_location(self):
        subscribe(self.args_url, self.args_api_key, self.signals, on_subscribe=self.redirect_location_to_emulator, on_change=False)


if __name__ == "__main__":
    adb_device = adb.get_emulator_device()
    br_emu = brokerToEmu(adb_device)
    br_emu.update_emu_location()
