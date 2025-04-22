import libs.adb.device as adb
import libs.vhal_emulator.vhal_emulator as vhal_emu
from libs.vhal_emulator.vhal_prop_consts_2_0 import vhal_props, vhal_vehicle_area
from libs.remotive.subscribe import parsing_to_subscribe, subscribe, get_proper_signal_value
from inspect import getmembers


class brokerDeviceBridge:
    def __init__(self, adb_dev):
        # Get the connected device via adb only once
        self.adb_dev = adb_dev
        self.vhal = vhal_emu.Vhal()

    def redirect_vhal_props_to_device(self, signals):
        for signal in signals:
            signal_val = get_proper_signal_value(signal)
            print(
                "{} {} {} ".format(
                    signal.id.name, signal.id.namespace.name, signal_val
                )
            )
            for prop in getmembers(vhal_props):
                if signal.id.name in prop[0]:
                    # As Oct 2023, Remotive Labs Brokers support vehicle areas of type GLOBAL only.
                    # In the future it'd be nice to get such info without hard coding it.
                    # Refer to https://developer.android.com/reference/android/car/VehicleAreaType.
                    print("Setting property on AAOS...")
                    self.vhal.set_property(signal.id.name, vhal_vehicle_area.GLOBAL, signal_val)

    def set_vhal_props(self):
        args_url, args_api_key, _cvd, signals = parsing_to_subscribe()
        subscribe(args_url, args_api_key, signals, on_subscribe=self.redirect_vhal_props_to_device, on_change=False)


if __name__ == "__main__":
    # adb_device = adb.get_device()
    # Use the following line to communicate with emulator, and the previous one with AAOS Pixel
    adb_device = adb.get_emulator_device()
    br_dev = brokerDeviceBridge(adb_device)
    br_dev.set_vhal_props()
