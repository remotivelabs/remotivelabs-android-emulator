from __future__ import annotations

from android_bridge.br_location_to_cuttlefish import BrokerToCuttlefish

import argparse
import asyncio

import structlog
from remotivelabs.broker import BrokerClient
from remotivelabs.broker.auth import ApiKeyAuth
from remotivelabs.broker.frame import Frame
from remotivelabs.topology.namespaces.filters import FrameFilter
from remotivelabs.topology.namespaces.scripted import ScriptedNamespace
from remotivelabs.topology.namespaces.namespace_client import NamespaceClient

from android_bridge.signal_mapping import parse_signal_mappings

from .br_generic_props_to_aaos import BrokerToAAOS
from .br_location_to_emu import BrokerToEmu
from .libs.adb.adb_emulator import AndroidEmulator

logger = structlog.get_logger(__name__)


class AndroidBridge:
    def __init__(self, args) -> None:
        signal_mappings = (
            parse_signal_mappings(args.signal_mappings_file) if args.with_vhal else {}
        )
        self.br_emu = None
        self.br_cuttlefish = None
        self.br_prop = None

        if args.virtual_device_type == "android_emulator":
            android_emulator = AndroidEmulator(emulator_name=args.emulator_name)
            if args.with_location:
                self.br_emu = BrokerToEmu(
                    android_emulator,
                    longitude_signal_name=args.longitude_signal_name,
                    latitude_signal_name=args.latitude_signal_name,
                )

            if args.with_vhal:
                self.br_prop = BrokerToAAOS(android_emulator, signal_mappings)

        if args.virtual_device_type == "cuttlefish":
            if args.with_location:
                self.br_cuttlefish = BrokerToCuttlefish(
                    args.cuttlefish_url,
                    longitude_signal_name=args.longitude_signal_name,
                    latitude_signal_name=args.latitude_signal_name,
                )

        self.broker_client = BrokerClient(url=args.url, auth=ApiKeyAuth(args.api_key))
        android_namespace = ScriptedNamespace(
            "android", self.broker_client, decode_named_values=True
        )

        input_handlers = []
        if args.with_location:
            location_handler = android_namespace.create_input_handler(
                filters=[
                    FrameFilter(frame_name=args.longitude_signal_name),
                    FrameFilter(frame_name=args.latitude_signal_name),
                ],
                callback=self._handle_location,
            )
            input_handlers.append(location_handler)

        if args.with_vhal:
            filter_names = args.signal if args.signal else signal_mappings.keys()
            filters = [FrameFilter(frame_name=name) for name in filter_names]
            property_handler = android_namespace.create_input_handler(
                filters=filters,
                callback=self._handle_property,
            )
            input_handlers.append(property_handler)

        self.namespace_client = NamespaceClient(
            broker_client=self.broker_client,
            namespaces=[android_namespace],
            input_handlers=input_handlers,
        )

    async def _handle_location(self, frame: Frame):
        # logger.info("received location", frame=frame)
        if self.br_emu is not None:
            self.br_emu.redirect_location_signals_to_emulator(frame.name, frame.value)
        if self.br_cuttlefish:
            self.br_cuttlefish.redirect_location_signals_to_cuttlefish(
                frame.name, frame.value
            )

    async def _handle_property(self, frame: Frame):
        # logger.info("received property", frame=frame)
        if self.br_prop:
            self.br_prop.update_property(frame.name, frame.value)

    async def run(self):
        await self.namespace_client.start()
        await self.namespace_client.run_forever()


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


async def main(args):
    bridge = AndroidBridge(args)
    await bridge.run()


if __name__ == "__main__":
    args = parse_arguments()
    asyncio.run(main(args))
