#!/usr/bin/env bash

ulimit -n 4096 # Increase open files limit for launch_cvd

./run_services.sh & # Existing orchestrator startup script

sleep 5

./bin/adb devices
./bin/launch_cvd --daemon \
  --resume=false \
  --guest_enforce_security=false \
  --enable_vhal_proxy_server \
  --display=width=1400,height=800,dpi=160,refresh_rate_hz=30 \
  --display=width=600,height=800,dpi=160,refresh_rate_hz=30 \
  --report_anonymous_usage_stats=n
sleep 2

./bin/adb connect localhost:6520
./bin/adb wait-for-device
./bin/adb root

for apk in apks/*.apk; do
  ./bin/adb install "$apk"
done

./bin/adb shell svc wifi enable
./bin/adb shell cmd wifi connect-network VirtWifi open
./bin/adb shell cmd car_service enable-uxr false # Allow apps to be used while driving

socat TCP-LISTEN:9300,fork,reuseaddr,bind=$(hostname -i) TCP:192.168.98.1:9300 & # Redirect from container port to vhal_proxy_server port

echo "Cuttlefish is started and ready to use"

# To keep it running
tail -f /dev/null
