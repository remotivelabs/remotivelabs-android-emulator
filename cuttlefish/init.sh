#!/usr/bin/env bash

./run_services.sh & # Existing orchestrator startup script

sleep 5

./bin/adb devices
if [ ! -f "container_first_start" ]; then
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

  if [ "$(./bin/adb shell service check car_service)" = "found" ]; then
    # Detect if android has car_service so we know to wait for it later
    touch "has_car_service"
  fi

  ./bin/adb reboot # This is needed when the APKs contain a map app that should take the center spot
  touch "container_first_start"
else
  ./bin/launch_cvd --daemon \
    --guest_enforce_security=false \
    --enable_vhal_proxy_server \
    --display=width=1408,height=792,dpi=160,refresh_rate_hz=30 \
    --display=width=600,height=800,dpi=160,refresh_rate_hz=30 \
    --report_anonymous_usage_stats=n
  sleep 2
  ./bin/adb connect localhost:6520
  ./bin/adb shell service check car_service
fi

./bin/adb wait-for-device
./bin/adb root

echo -n "Waiting for Android to finish booting"
while [ "$(./bin/adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" != "1" ]; do
  echo -n "."
  sleep 2
done

./bin/adb shell svc wifi enable
./bin/adb shell cmd wifi connect-network VirtWifi open

if [ ! -f "has_car_service" ]; then
  while ! ./bin/adb shell cmd -l | grep -q "car_service"; do
    echo -n "."
    sleep 1
  done
  ./bin/adb shell cmd car_service enable-uxr false # Allow apps to be used while driving
fi
echo ""

socat TCP-LISTEN:9300,fork,reuseaddr,bind=$(hostname -i) TCP:192.168.98.1:9300 & # Redirect from container port to vhal_proxy_server port

echo "Cuttlefish is started and ready to use"

# To keep it running
tail -f /dev/null
