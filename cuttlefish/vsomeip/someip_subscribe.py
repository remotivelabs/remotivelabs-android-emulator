#!/usr/bin/env python3
"""
Minimal SOME/IP eventgroup subscriber for testing the RemotiveLabs broker.

Sends a SubscribeEventgroup (SOME/IP-SD) to the server, prints the Ack/Nack,
and prints any events the server then pushes.

Requires scapy:  apt-get install -y python3-scapy   (or: pip install scapy)

The host running this must have an IP on the SOME/IP vlan (172.31.0.0/24) and
be able to reach the server. Easiest options:
  * a throwaway container on the network:
      docker run --rm -it --network <proj>_SOMEIP --ip 172.31.0.50 \
        -v "$PWD/vsomeip:/x" python:3.12-slim \
        sh -c 'pip install -q scapy && python /x/someip_subscribe.py 172.31.0.50 0x66 0x143'
  * the cuttlefish container itself (add a temp vlan IP first):
      docker exec cuttlefish ip addr add 172.31.0.50/24 dev someip
      docker exec cuttlefish python3 /root/someip_subscribe.py 172.31.0.50 0x66 0x143

Usage:  someip_subscribe.py <client_ip> <service_hex> <eventgroup_hex> [server_ip]

Service / eventgroup IDs for this rig (server 172.31.0.18, data UDP 16000):
  0x64 TurnlightIndicator  eg 0x141      0x67 HVAC/CompartmentControl eg 0x144
  0x65 LocationService     eg 0x142      0x68 GearService             eg 0x145
  0x66 SpeedService        eg 0x143
"""
import socket, sys, time, threading
from scapy.contrib.automotive.someip import (
    SOMEIP, SD, SDEntry_EventGroup, SDOption_IP4_EndPoint)

if len(sys.argv) < 4:
    sys.exit(__doc__)
CLIENT_IP  = sys.argv[1]
SERVICE    = int(sys.argv[2], 0)
EVENTGROUP = int(sys.argv[3], 0)
SERVER_IP  = sys.argv[4] if len(sys.argv) > 4 else "172.31.0.18"
SD_PORT    = 30490
INSTANCE   = 0x0001
EVENT_PORT = 30509          # where we ask the server to send events

def subscribe_pkt(session):
    return bytes(
        SOMEIP(srv_id=0xFFFF, sub_id=1, event_id=0x100, client_id=0,
               session_id=session, proto_ver=1, iface_ver=1,
               msg_type=0x02, retcode=0) /
        SD(flags=0xC0,                                   # reboot + unicast
           entry_array=[SDEntry_EventGroup(
               type=6, n_opt_1=1, srv_id=SERVICE, inst_id=INSTANCE,
               major_ver=0, ttl=0xFFFFFF, cnt=0, eventgroup_id=EVENTGROUP)],
           option_array=[SDOption_IP4_EndPoint(
               type=0x04, addr=CLIENT_IP, l4_proto=0x11, port=EVENT_PORT)]))

# Receive events on the endpoint we advertise.
evsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
evsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
evsock.bind((CLIENT_IP, EVENT_PORT))
def rx_events():
    while True:
        data, addr = evsock.recvfrom(4096)
        p = SOMEIP(data)
        print(f"  EVENT  svc=0x{p.srv_id:04x} id=0x{p.event_id:04x} "
              f"payload={bytes(p.payload).hex()}", flush=True)
threading.Thread(target=rx_events, daemon=True).start()

# SD socket: send the subscribe (and refresh it), read the Ack/Nack.
sdsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sdsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sdsock.bind((CLIENT_IP, SD_PORT))
print(f"Subscribing svc=0x{SERVICE:04x} eg=0x{EVENTGROUP:04x} to {SERVER_IP}:{SD_PORT}; "
      f"events -> {CLIENT_IP}:{EVENT_PORT}", flush=True)
def refresh():
    s = 1
    while True:
        sdsock.sendto(subscribe_pkt(s), (SERVER_IP, SD_PORT))
        s += 1
        time.sleep(5)
threading.Thread(target=refresh, daemon=True).start()

while True:
    data, _ = sdsock.recvfrom(4096)
    sd = SOMEIP(data)[SD]
    for e in sd.entry_array:
        kind = "ACK" if getattr(e, "ttl", 0) else "NACK(rejected)"
        print(f"  SD {kind}: svc=0x{e.srv_id:04x} eg=0x{getattr(e,'eventgroup_id',0):04x} "
              f"ttl={e.ttl}", flush=True)
