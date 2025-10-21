from __future__ import annotations

import asyncio

import structlog
from remotivelabs.broker import BrokerClient
from remotivelabs.broker.auth import ApiKeyAuth
from remotivelabs.broker.frame import Frame
from remotivelabs.topology.namespaces.filters import FrameFilter
from remotivelabs.topology.namespaces.namespace_client import NamespaceClient
from remotivelabs.topology.namespaces.scripted import ScriptedNamespace

from .arguments import parse_arguments
from .broker_to_cuttlefish import BrokerToCuttlefish
from .broker_to_emulator import BrokerToEmulator
from .signal_mapping import parse_signal_mappings

logger = structlog.get_logger(__name__)


class AndroidBridge:
    """
    Manages connections and signal routing between the broker client and Android virtual devices
    (Android Emulator or Cuttlefish), handling location and vehicle property signals as configured.
    """

    def __init__(self, args) -> None:
        signal_mappings = (
            parse_signal_mappings(args.signal_mappings_file) if args.with_vhal else {}
        )
        self.br_emulator = None
        self.br_cuttlefish = None

        if args.virtual_device_type == "android_emulator":
            self.br_emulator = BrokerToEmulator(
                emulator_name=args.emulator_name,
                longitude_signal_name=args.longitude_signal_name,
                latitude_signal_name=args.latitude_signal_name,
                signal_mappings=signal_mappings,
            )

        if args.virtual_device_type == "cuttlefish":
            self.br_cuttlefish = BrokerToCuttlefish(
                cuttlefish_gnss_url=args.cuttlefish_gnss_url,
                cuttlefish_vhal_url=args.cuttlefish_vhal_url,
                longitude_signal_name=args.longitude_signal_name,
                latitude_signal_name=args.latitude_signal_name,
                signal_mappings=signal_mappings,
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
        if self.br_emulator is not None:
            self.br_emulator.redirect_location_signals_to_emulator(
                frame.name, frame.value
            )
        if self.br_cuttlefish:
            self.br_cuttlefish.redirect_location_signals_to_cuttlefish(
                frame.name, frame.value
            )

    async def _handle_property(self, frame: Frame):
        # logger.info("received property", frame=frame)
        if self.br_emulator:
            self.br_emulator.update_property(frame.name, frame.value)

        if self.br_cuttlefish:
            self.br_cuttlefish.update_property(frame.name, frame.value)

    async def run(self):
        await self.namespace_client.start()
        await self.namespace_client.run_forever()


async def main(args):
    bridge = AndroidBridge(args)
    await bridge.run()


if __name__ == "__main__":
    args = parse_arguments()
    asyncio.run(main(args))
