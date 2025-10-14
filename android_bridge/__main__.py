from __future__ import annotations

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
        signal_mappings = parse_signal_mappings(args.signal_mappings_file)
        android_emulator = AndroidEmulator(emulator_name=args.emulator_name)

        self.br_emu = BrokerToEmu(
            android_emulator,
            longitude_signal_name=args.longitude_signal_name,
            latitude_signal_name=args.latitude_signal_name,
        )
        self.br_prop = BrokerToAAOS(android_emulator, signal_mappings)

        self.broker_client = BrokerClient(url=args.url, auth=ApiKeyAuth(args.api_key))
        android_namespace = ScriptedNamespace(
            "android", self.broker_client, decode_named_values=True
        )

        location_handler = android_namespace.create_input_handler(
            filters=[
                FrameFilter(frame_name=args.longitude_signal_name),
                FrameFilter(frame_name=args.latitude_signal_name),
            ],
            callback=self._handle_location,
        )

        filters = list(map(lambda x: FrameFilter(frame_name=x), signal_mappings.keys()))
        property_handler = android_namespace.create_input_handler(
            filters=filters,
            callback=self._handle_property,
        )

        self.namespace_client = NamespaceClient(
            broker_client=self.broker_client,
            namespaces=[android_namespace],
            input_handlers=[location_handler, property_handler],
        )

    async def _handle_location(self, frame: Frame):
        # logger.info("received location", frame=frame)
        self.br_emu.redirect_location_signals_to_emulator(frame.name, frame.value)

    async def _handle_property(self, frame: Frame):
        # logger.info("received property", frame=frame)
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
        "--signal-mappings-file",
        type=str,
        required=True,
        metavar="/path/to/file.json",
        help="JSON file containing signal to signal mappings (array of objects format)",
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
        "--emulator-name",
        type=str,
        required=False,
        default="emulator-5554",
        metavar="emulator-5554",
        help="Name of the android emulator (see 'adb devices')",
    )

    return parser.parse_args()


async def main(args):
    bridge = AndroidBridge(args)
    await bridge.run()


if __name__ == "__main__":
    args = parse_arguments()
    asyncio.run(main(args))
