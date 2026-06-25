#!/usr/bin/env bash
# Increase open files limit for launch_cvd
ulimit -n 4096

# Existing orchestrator startup script
./run_services.sh &

# Wait for orchestrator to start
until nc -z localhost 2081 2>/dev/null; do sleep 1; done
sleep 5

mkdir -p state/images
cp -n bootloader state/images
cp -n *.img state/images

# Launch Cuttlefish image.
#
# --enable_modem_simulator=false drops the *host* modem simulator. We route
# everything over Wi-Fi (VirtWifi), so cellular is unused. NOTE: this alone does
# NOT stop the cellular reboot loop — the guest's minradio HAL still presents a
# registered LTE network, so telephony keeps attempting data calls regardless.
# The actual fix is disabling mobile data after boot (see below).
./bin/adb devices
./bin/launch_cvd --daemon \
  --vhost_user_vsock=false \
  --instance_dir=/root/state/ \
  --system_image_dir=/root/state/images \
  --gpu_mode=${CUTTLEFISH_GPU_MODE:-auto} \
  --memory_mb=${CUTTLEFISH_MEMORY_MB:-4096} \
  --cpus=${CUTTLEFISH_CPUS:-2} \
  --guest_enforce_security=false \
  --enable_modem_simulator=false \
  --display=${CUTTLEFISH_DISPLAY_MAIN:-width=1400,height=800,dpi=160,refresh_rate_hz=30} \
  --display=${CUTTLEFISH_DISPLAY_CLUSTER:-width=600,height=800,dpi=160,refresh_rate_hz=30} \
  --report_anonymous_usage_stats=n
sleep 3

./bin/adb connect localhost:6520
./bin/adb wait-for-device
./bin/adb root
./bin/adb wait-for-device

# Kill the cellular data-call retry storm.
#
# The guest's minradio HAL advertises a registered LTE network, but the data
# call never provisions, so telephony retries it with ~0ms backoff. Every retry
# registers a NetworkAgent, and registering one trips a latent libbinder bug
# (bad_variant_access in onNetworkCreated -> handleRegisterNetworkAgent) that
# aborts system_server — the guest then reboots, and the loop repeats. We don't
# use cellular, so disable mobile data. Persist it in the settings DB (read
# early at boot) AND issue the runtime svc call, so the storm is suppressed both
# now and on subsequent boots. NOTE: the underlying libbinder bad_variant_access
# is a binder/ABI skew in this build and is the real bug; this only removes its
# trigger.
./bin/adb shell settings put global mobile_data 0
./bin/adb shell svc data disable

# Install optional APKs
for apk in apks/*.apk; do
  ./bin/adb install "$apk"
done

# Enable wifi and connect to network
./bin/adb shell svc wifi enable
./bin/adb shell cmd wifi connect-network VirtWifi open

# Lower MTU in case network does not support default 1500
./bin/adb shell ip link set mtu 1400 dev wlan0

# Fix internet connectivity in the Cuttlefish instance by masquerading outgoing packets from eth0
# (ip_forward is required for the MASQUERADE to forward; it previously got enabled
# as a side effect of the SOME/IP proxy-ARP setup, which the L2 bridge below no
# longer needs — so set it explicitly here).
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# Allow apps to be used while driving
until
  ./bin/adb shell service list | grep -q car_service
do
  echo "Waiting for car_service"
  sleep 5
done
./bin/adb shell cmd car_service enable-uxr false
sleep 5

# Enable Car info in the cluster panel
./bin/adb shell pm grant android.car.cluster android.car.permission.CAR_ENERGY
./bin/adb shell pm grant android.car.cluster android.car.permission.CAR_SPEED
./bin/adb shell am force-stop android.car.cluster

# Reroute container port 9300 to internal VHAL proxy server.
# Bind to the container's default-route (eth0) address instead of
# $(hostname -i): when started with --ip 172.31.0.12 that name resolves to the
# guest's SOME/IP address, which we hand over to the guest below (so the bind
# would fail), and a wildcard bind would collide with vhal_proxy_server's
# 192.168.98.1:9300.
HOST_IP=$(ip -4 route get 1.1.1.1 2>/dev/null | sed -n 's/.*src \([0-9.]*\).*/\1/p')
socat TCP-LISTEN:9300,fork,reuseaddr,bind=${HOST_IP} TCP:192.168.98.1:9300 &

# ---------------------------------------------------------------------------
# SOME/IP bridging
#
# Make the Android guest reachable on the Docker SOME/IP network as
# 172.31.0.12 with NO NAT, so it can both send SOME/IP requests AND receive
# server->client events/notifications from the service container (172.31.0.18),
# INCLUDING SOME/IP-SD multicast (224.0.55.55) — which a routed/proxy-ARP path
# cannot carry, but an L2 bridge does natively.
#
# The Android image owns the GUEST side: it moves the guest's wired NIC (eth0)
# into a dedicated "someip" network namespace, gives it 172.31.0.12/24 on-link,
# and adds a `224.0.0.0/4 dev eth0` route. That route is REQUIRED on the guest:
# vsomeip will not start service discovery (will not bind UDP 30490) until the
# interface is routable, and it needs the route to egress SD multicast. That
# namespace is invisible to Android's netd, so its config is never flushed by
# Wi-Fi churn. This script only wires up the container side.
#
# Topology (single Cuttlefish instance):
#   - Docker SOME/IP net : 172.31.0.0/24, gw .253, vlan 123. Inside this
#       container it is the 802.1Q interface "someip" (someip@corenetwork; NOT
#       eth0 — eth0 is the internet path, 172.16.x).
#   - Guest eth0 (in its "someip" netns, 172.31.0.12/24 on-link) is wired to
#       this container's tap cvd-mtap-01, which carries ONLY that netns's eth0.
#
# Method: L2 bridge. someip (the vlan-123 iface) and cvd-mtap-01 (the guest tap)
# are enslaved to one bridge, putting the guest and the server 172.31.0.18 on a
# single broadcast domain. ARP, unicast AND multicast then flood natively — no
# proxy-ARP, no /32 routes, no NAT exemption, and no multicast router/daemon.
# Multicast snooping is disabled so the SD group floods without an IGMP querier.
# The vlan iface still does the 802.1Q tagging; only untagged frames are bridged.
# ---------------------------------------------------------------------------
SOMEIP_IFACE=someip            # this container's 802.1Q iface on the SOME/IP vlan
SOMEIP_GUEST_IP=172.31.0.12    # address the guest owns on the SOME/IP net
GUEST_TAP=cvd-mtap-01          # this container's tap the guest eth0 sits on
SOMEIP_BR=someipbr             # L2 bridge joining the vlan iface and the guest tap

setup_someip_bridge() {
  # Create the bridge (idempotent across the re-assert loop below).
  ip link add name ${SOMEIP_BR} type bridge 2>/dev/null
  # STP off (2 ports, no loop possible) so ports forward immediately; disable
  # multicast snooping so the SD group (224.0.55.55) floods to the guest without
  # an IGMP querier on the segment.
  echo 0 > /sys/class/net/${SOMEIP_BR}/bridge/stp_state 2>/dev/null
  echo 0 > /sys/class/net/${SOMEIP_BR}/bridge/multicast_snooping 2>/dev/null
  # Keep bridging at pure L2: if br_netfilter is loaded, don't divert bridged IP
  # frames into iptables (would re-expose the guest to Cuttlefish's MASQUERADE).
  echo 0 > /proc/sys/net/bridge/bridge-nf-call-iptables 2>/dev/null || true

  # Address Docker put on the vlan iface:
  #   --ip 172.31.0.12 -> it belongs to the GUEST; drop it so only the guest
  #                       answers for it across the bridge.
  #   --ip 172.31.0.13 -> it's the container's own clean vlan source; move it
  #                       onto the bridge so the container keeps an address on the
  #                       segment (an enslaved port must not hold an IP).
  local ipcidr
  ipcidr=$(ip -4 -o addr show dev ${SOMEIP_IFACE} | awk '{print $4}')
  if [ -n "$ipcidr" ]; then
    ip addr del "$ipcidr" dev ${SOMEIP_IFACE}
    case "$ipcidr" in
      ${SOMEIP_GUEST_IP}/*) : ;;
      *) ip addr replace "$ipcidr" dev ${SOMEIP_BR} ;;
    esac
  fi

  # Enslave both legs and bring everything up. Idempotent — also re-asserts the
  # port if RIL has bounced the tap (see loop below).
  ip link set ${SOMEIP_IFACE} master ${SOMEIP_BR}
  ip link set ${GUEST_TAP}    master ${SOMEIP_BR}
  ip link set ${SOMEIP_IFACE} up
  ip link set ${GUEST_TAP}    up
  ip link set ${SOMEIP_BR}    up
}

setup_someip_bridge

# Cuttlefish's RIL reconfigures cvd-mtap-01 shortly after boot (it resets L3 state
# on the tap). Master enslavement is L2 and should survive that, but if RIL bounces
# the tap down/up the bridge port can drop — re-assert a handful of times over the
# first ~2 min to win that race (one-shot event, not a perpetual loop).
( for _ in 1 2 3 4 5 6; do sleep 20; setup_someip_bridge; done ) &

echo "Cuttlefish is started and ready to use"

# To keep it running
sleep infinity &
blocked_pid=$!

stop_cuttlefish() {
  ./bin/adb reboot
  ./bin/stop_cvd
  kill -TERM "$blocked_pid" 2>/dev/null
  exit 0
}

trap stop_cuttlefish INT TERM

wait "$blocked_pid"
stop_cuttlefish
