import libs.adb.device as adb
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
        print("Available VHAL properties:", self.vhal._propToType)

    def redirect_vhal_props_to_device(self, signals):
        for signal in signals:
            signal_val = get_proper_signal_value(signal)
            print(
                "{} {} {} {}".format(
                    signal.id.name, signal.id.namespace.name, signal_val, type(signal_val)
                )
            )
            for prop in getmembers(vhal_props):
                if signal.id.name in prop[0]:
                    # As Oct 2023, Remotive Labs Brokers support vehicle areas of type GLOBAL only.
                    # In the future it'd be nice to get such info without hard coding it.
                    # Refer to https://developer.android.com/reference/android/car/VehicleAreaType.
                    print("Setting property on AAOS...")
                    property_id = 291504647  # The property ID you want to set
                    area_id = vhal_vehicle_area.GLOBAL  # Try GLOBAL first; if no effect, try 0
                    value = round(signal_val, 1)
                    self.vhal.set_property(property_id, area_id, value)
                    property_id = 291504648  # The property ID you want to set
                    area_id = vhal_vehicle_area.GLOBAL  # Try GLOBAL first; if no effect, try 0
                    value = round(signal_val, 1)
                    self.vhal.set_property(property_id, area_id, value)

                    #self.vhal.set_property(0x15600503, vhal_vehicle_area.GLOBAL, 1001.0)

    def set_vhal_props(self):
        args_url, args_api_key, _cvd, signals = parsing_to_subscribe()
        subscribe(args_url, args_api_key, signals, on_subscribe=self.redirect_vhal_props_to_device, on_change=True)


if __name__ == "__main__":
    # adb_device = adb.get_device()
    # Use the following line to communicate with emulator, and the previous one with AAOS Pixel
    adb_device = adb.get_emulator_device()
    br_dev = brokerDeviceBridge(adb_device)
    br_dev.set_vhal_props()

    for name, val in getmembers(vhal_props):
        if val == 291504647:
            print(f"Property name: {name}")
