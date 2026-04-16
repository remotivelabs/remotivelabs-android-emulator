#!/usr/bin/env bash
# Increase open files limit for launch_cvd
ulimit -n 4096

# Existing orchestrator startup script
service nginx start
service cuttlefish-host-resources start
service cuttlefish-operator start
service cuttlefish-host_orchestrator start

# Wait for orchestrator to start
until nc -z localhost 2081 2>/dev/null; do sleep 1; done
sleep 5

mkdir -p state/images
cp -n bootloader state/images
cp -n *.img state/images

# Launch Cuttlefish image
./bin/adb devices
./bin/launch_cvd --daemon \
  --vhost_user_vsock=false \
  --instance_dir=/root/state/ \
  --system_image_dir=/root/state/images \
  --gpu_mode=${CUTTLEFISH_GPU_MODE:-auto} \
  --memory_mb=${CUTTLEFISH_MEMORY_MB:-4096} \
  --guest_enforce_security=false \
  --enable_vhal_proxy_server \
  --display=${CUTTLEFISH_DISPLAY_MAIN:-width=1400,height=800,dpi=160,refresh_rate_hz=30} \
  --display=${CUTTLEFISH_DISPLAY_CLUSTER:-width=600,height=800,dpi=160,refresh_rate_hz=30} \
  --report_anonymous_usage_stats=n
sleep 3

./bin/adb connect localhost:6520
./bin/adb wait-for-device
./bin/adb root

# Install optional APKs
for apk in apks/*.apk; do
  ./bin/adb install "$apk"
done

# Enable wifi and connect to network
./bin/adb shell svc wifi enable
./bin/adb shell cmd wifi connect-network VirtWifi open

# Lower MTU in case network does not support default 1500
./bin/adb shell ip link set mtu 1400 dev wlan0

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

# Reroute container port 9300 to internal VHAL proxy server
socat TCP-LISTEN:9300,fork,reuseaddr,bind=$(hostname -i) TCP:192.168.98.1:9300 &

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
