# SOME/IP from the Android (Cuttlefish) guest

This directory holds the vsomeip client configuration the Android guest uses to
talk to the SOME/IP service container on the Docker `..._SOMEIP` network.

## What `init.sh` sets up

The guest presents on the Docker SOME/IP network as **`172.31.0.12`** with no
NAT, so it can both send requests and receive server→client
events/notifications. Topology for this rig:

| Thing | Value |
|---|---|
| Docker SOME/IP subnet | `172.31.0.0/24`, gw `172.31.0.253`, vlan 123 |
| Service container (server) | **`172.31.0.18`** (GWM broker) |
| Guest SOME/IP address | **`172.31.0.12/24`** (on `eth0`, in the guest's `someip` netns, on-link) |
| Container iface on SOME/IP net | `someip` (NOT `eth0`; `eth0` is the internet path) |
| Guest `eth0` ↔ container tap | `cvd-mtap-01` |
| Cuttlefish NAT location | **`iptables-legacy`** (`MASQUERADE -s 192.168.9x.x`) |

**The guest side is owned by the Android image, not `init.sh`.** The image moves
`eth0` into a dedicated **`someip` network namespace** and gives it
`172.31.0.12/24` on-link (no gateway). Because that namespace is invisible to
Android's `netd`, the route can never be flushed by Wi-Fi churn — so the route
is rock-stable with **no re-assert loop** (verified 20/20 with nothing running).
The vsomeip client must run **inside that namespace** (the image enters it via
`enter_namespace net /mnt/run/someip`, the same pattern Google ships for the
VHAL `auto_eth` ns).

`init.sh` only wires up the **container** side — **proxy-ARP in both directions**:
the guest is on-link, so it ARPs `172.31.0.18` directly on `cvd-mtap-01` (the
container answers via `proxy_arp` on that tap and forwards onto the vlan), and
the server's ARP for `172.31.0.12` on the vlan is answered by a proxy entry on
`someip`. Traffic is forwarded un-NATted (an `ACCEPT` exemption ahead of
Cuttlefish's legacy masquerade). This all lives in the container's own namespace,
so nothing disturbs it — no healer, no supervisor, no loop.

> Run with **`--ip 172.31.0.12`** (recommended). Docker reserves exactly that
> one address; on startup `init.sh` moves it off the container's `someip`
> interface onto the guest and leaves the container with no SOME/IP address of
> its own (it forwards via a link route + proxy-ARP). This reserves only the
> address you actually use.
>
> Do **not** drop `--ip` — Docker auto-assigns from the low end of the pool and
> will eventually hand `172.31.0.12` to the container itself, colliding with the
> guest. If you must use a different address, pick a fixed free one (e.g.
> `--ip 172.31.0.13`); `init.sh` then keeps that address on the container and
> still gives the guest `172.31.0.12` via proxy-ARP.

## Container A's SOME/IP offer (discovered from the topology)

Server `172.31.0.18`, data on **UDP 16000**. SD on `224.0.55.55:30490`.

| Service | ID | Instance | EventGroup | Event |
|---|---|---|---|---|
| TurnlightIndicator | `0x0064` (100) | `0x0001` | `0x0141` (321) | `0x03E9` |
| LocationService | `0x0065` (101) | `0x0001` | `0x0142` (322) | `0x03E9` |
| SpeedService | `0x0066` (102) | `0x0001` | `0x0143` (323) | `0x03EA` |
| **HVACService** (CompartmentControl) | `0x0067` (103) | `0x0001` | `0x0144` (324) | `0x03EB` |
| GearService | `0x0068` (104) | `0x0001` | `0x0145` (325) | `0x03EC` |

**Service `0x0067` (HVAC) is statically pushed by the broker to
`172.31.0.12:16000`** — i.e. it needs no service discovery and is the
designed `.18 ↔ .12` link. The other four are offered via SD multicast.
`vsomeip.json` therefore has `service-discovery.enable = false`.

> If you need the SD-multicast services (`0x64/0x65/0x66/0x68`) rather than just
> the statically-pushed `0x67`, the guest also needs **multicast forwarding**
> for `224.0.55.55` from the `someip` vlan onto `cvd-mtap-01` (e.g. `smcroute`
> in the container), which `init.sh` does not set up. Ask if you want that.

## Using the config in the guest

The vsomeip client must run **inside the `someip` network namespace** (that's
where `eth0` / `172.31.0.12` lives). Bind it there via the image's
`enter_namespace net /mnt/run/someip` init pattern, or for a manual test:

```bash
adb push vsomeip/vsomeip.json /data/local/tmp/vsomeip.json
adb shell ip netns exec someip env VSOMEIP_CONFIGURATION=/data/local/tmp/vsomeip.json <your-client>
```

`unreliable` is the remote service's UDP port (16000). Adjust `applications`
`name`/`id` and the per-service `events`/`is_field` flags to match your client.

## Verify

```bash
# guest -> server (run inside the someip netns; on-link, no -I needed)
adb shell ip netns exec someip ping -c3 172.31.0.18
# on the container, watch SOME/IP cross the vlan with source 172.31.0.12
tcpdump -nei someip host 172.31.0.18
# and arrive at the guest eth0 (inside the netns)
adb shell ip netns exec someip tcpdump -nei eth0 host 172.31.0.18
```
