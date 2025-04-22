import argparse
import math
import time
import remotivelabs.broker.sync as br
import queue
from threading import Thread
import grpc

from typing import Callable, Generator, Sequence, Tuple


def _open_subscription_thread(
    broker,
    client_id: br.common_pb2.ClientId,
    network_stub: br.network_api_pb2_grpc.NetworkServiceStub,
    signals: br.network_api_pb2.Signals,
    on_subscribe: Callable[[Sequence[br.network_api_pb2.Signal]], None],
    on_change: bool = False,
) -> grpc.RpcContext:
    sync = queue.Queue()
    Thread(
        target=broker.act_on_signal,
        args=(
            client_id,
            network_stub,
            signals,
            on_change,  # True: only report when signal changes
            on_subscribe,
            lambda subscription: (sync.put(subscription)),
        ),
    ).start()
    # wait for subscription to settle
    subs = sync.get()
    return subs


def _subscribe_list(
    signal_creator, signals: list[Tuple[str, str]]
) -> Generator[br.common_pb2.SignalId, None, None]:
    for namespace, signal in signals:
        yield signal_creator.signal(signal, namespace)


def get_proper_signal_value(signal: br.network_api_pb2.Signal):
    if signal.raw != b"":
        return signal.raw
    elif signal.HasField("integer"):
        return signal.integer
    elif signal.HasField("double"):
        return signal.double
    elif signal.HasField("arbitration"):
        return signal.arbitration
    else:
        return "empty"


def printer(signals: br.network_api_pb2.Signals) -> None:
    for signal in signals:
        print(
            "{} {} {}".format(
                signal.id.name, signal.id.namespace.name, str(get_proper_signal_value(signal))
            )
        )


def subscribe(
    url: str,
    x_api_key: str,
    signals: list[Tuple[str, str]],
    on_subscribe: Callable[[Sequence[br.network_api_pb2.Signal]], None],
    on_change: bool,
) -> None:
    # gRPC connection to RemotiveBroker
    intercept_channel = br.create_channel(url, x_api_key)
    system_stub = br.system_api_pb2_grpc.SystemServiceStub(intercept_channel)
    network_stub = br.network_api_pb2_grpc.NetworkServiceStub(intercept_channel)
    br.check_license(system_stub)

    # Generate a list of values ready for subscribe
    subscribe_values = list(_subscribe_list(br.SignalCreator(system_stub), signals))
    if len(subscribe_values) == 0:
        print("No signals found. Nothing to do...")
        return

    client_id_name = "MySubscriber_{}".format(math.floor(time.monotonic()))
    client_id: br.common_pb2.ClientId = br.common_pb2.ClientId(id=client_id_name)

    print("Subscribing on signals...")

    subscription = _open_subscription_thread(br, client_id, network_stub, subscribe_values, on_subscribe, on_change)

    try:
        while True:
            pass
    except KeyboardInterrupt:
        subscription.cancel()
        print("Keyboard interrupt received. Closing scheduler.")


class NamespaceArgument(argparse.Action):
    def __call__(self, _parser, namespace, value, _option):
        print("Select namespace:", value)
        setattr(namespace, "namespace", value)


class SignalArgument(argparse.Action):
    def __call__(self, _parser, namespace, value, _option):
        ns = getattr(namespace, "namespace")
        if not ns:
            raise Exception(f'Namespace must be specified before signal ("{value}")')
        namespace.accumulated.append((ns, value))


def parsing_to_subscribe():
    parser = argparse.ArgumentParser(description="Provide address to RemotiveBroker")

    parser.add_argument(
        "-u",
        "--url",
        help="URL of the RemotiveBroker",
        type=str,
        required=False,
        default="http://127.0.0.1:50051",
    )

    parser.add_argument(
        "-x",
        "--x_api_key",
        help="API key is required when accessing brokers running in the cloud",
        type=str,
        required=False,
        default="offline",
    )

    parser.add_argument(
        "-n",
        "--namespace",
        help="Namespace to select frames on",
        type=str,
        action=NamespaceArgument,
        required=True,
    )

    parser.add_argument(
        "-s",
        "--signal",
        help="Signal to subscribe to",
        required=True,
        type=str,
        dest="accumulated",
        action=SignalArgument,
        default=[],
    )

    parser.add_argument(
        "-cvd_url",
        "--cuttlefish_url",
        help="Cuttlefish virtual Android device url, eg https://localhost:1443/devices/cvd-1",
        required=False,
        type=str,
        default="http://please_provide_cuttlefish_url",
    )

    try:
        args = parser.parse_args()
    except Exception as e:
        return print("Error specifying signals to use:", e)
    signals = args.accumulated

    return [args.url, args.x_api_key, args.cuttlefish_url, signals]
