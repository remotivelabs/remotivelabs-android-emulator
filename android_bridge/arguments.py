import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Forward signals from broker to Android Automotive OS via VHAL"
    )
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="URL of the RemotiveBroker",
    )
    parser.add_argument(
        "--api-key", type=str, required=True, help="API key for broker access"
    )
    parser.add_argument(
        "--with-location",
        type=bool,
        required=False,
        default=False,
        action=argparse.BooleanOptionalAction,
        help="If bridge should subscribe for longitude and latidude updates",
    )
    parser.add_argument(
        "--longitude-signal-name",
        type=str,
        required=False,
        default="LONGITUDE",
        metavar="LONGITUDE",
        help="Name of the latitude signal",
    )
    parser.add_argument(
        "--latitude-signal-name",
        type=str,
        required=False,
        default="LATITUDE",
        metavar="LATITUDE",
        help="Name of the latitude signal",
    )
    parser.add_argument(
        "--with-vhal",
        type=bool,
        required=False,
        default=False,
        action=argparse.BooleanOptionalAction,
        help="If bridge should subscribe for vhal properties",
    )
    parser.add_argument(
        "--signal",
        type=str,
        action="append",
        required=False,
        metavar="PERF_VEHICLE_SPEED",
        help="Name of vhal property signal to subscribe to. If this argument is not supplied it will subscribe to all signals in the mapping file",
    )
    parser.add_argument(
        "--signal-mappings-file",
        type=str,
        required=False,
        metavar="/path/to/file.json",
        help="JSON file containing signal to signal mappings (array of objects format). Required when --with-vhal is used",
    )
    parser.add_argument(
        "--virtual-device-type",
        type=str,
        choices=["android_emulator", "cuttlefish"],
        required=False,
        default="android_emulator",
        help="If android emulator or cuttlefish should be used",
    )
    parser.add_argument(
        "--emulator-name",
        type=str,
        required=False,
        default="emulator-5554",
        metavar="emulator-5554",
        help="Name of the android emulator (see 'adb devices')",
    )
    parser.add_argument(
        "--cuttlefish-url",
        type=str,
        required=False,
        default="https://localhost:1443/devices/cvd-1",
        metavar="https://localhost:1443/devices/cvd-1",
        help="Name of the android emulator (see 'adb devices')",
    )
    args = parser.parse_args()

    if args.with_vhal and not args.signal_mappings_file:
        parser.error("--signal-mappings-file is required when --with-vhal is used")

    if args.with_vhal and args.virtual_device_type == "cuttlefish":
        parser.error(
            "--virtual-device-type=cuttlefish is not supported for vhal properties"
        )

    return args
