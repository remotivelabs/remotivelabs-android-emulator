#!/usr/bin/env bash

# Increase open files limit for launch_cvd
ulimit -n 4096

# Existing orchestrator startup script
./run_services.sh &

# Wait for orchestrator to start
until nc -z localhost 2081 2>/dev/null; do sleep 1; done
sleep 5

# Launch Cuttlefish image
./bin/adb devices
./bin/launch_cvd --daemon \
  --guest_enforce_security=false \
  --enable_vhal_proxy_server \
  --display=width=1400,height=800,dpi=160,refresh_rate_hz=30 \
  --display=width=600,height=800,dpi=160,refresh_rate_hz=30 \
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

# Allow apps to be used while driving
until
  ./bin/adb shell service list | grep -q car_service
do
  echo "Waiting for car_service"
  sleep 5
done
# Extra sleep to ensure car service is up
sleep 10
./bin/adb shell cmd car_service enable-uxr false

# Reroute container port 9300 to internal VHAL proxy server
socat TCP-LISTEN:9300,fork,reuseaddr,bind=$(hostname -i) TCP:192.168.98.1:9300 &

echo "Cuttlefish is started and ready to use"

# To keep it running
tail -f /dev/null
