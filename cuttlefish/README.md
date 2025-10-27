# Cuttlefish

## Build

This Dockerfile will build a docker image capable of running a Android Automotive Cuttlefish instance (trout). It requires that you have already built the Cuttlefish image. To make it run within the standard cuttlefish-orchestrator for this example there needs to be a couple of minor tweaks of the build.

To get started building your own version, follow this guide: <https://source.android.com/docs/devices/cuttlefish/get-started> and <https://source.android.com/docs/automotive/virtualization/reference_platform>.

If you do not wish to build your own android version you can download a pre-built image from [ci.android.com](https://ci.android.com/builds/branches/aosp-android-latest-release/grid?legacy=1) but these are "phone" builds and do not support VHAL properties.

#### Disable internal VHAL server

To be able to pass VHAL properties from the host it needs to be configured to run the `vhal_proxy_server`. This is done during startup for Android to actually use it you need to build the image with the fake vhal server disabled. Update `/device/google/trout/aosp_trout_x86_64.mk` (depending on the architecture) and change the value of `ENABLE_VHAL_FAKE_GRPC_SERVER` to `false`.

```
ENABLE_VHAL_FAKE_GRPC_SERVER ?= false
```

The cuttlefish build is hardcoded to use the connection details of the fake vhal server so you will also need to change the `cid` and `port` in `/device/google/trout/trout_x86_64/BoardConfig.mk` (depending on the architecture) and set them as

```
BOARD_KERNEL_CMDLINE += androidboot.vendor.vehiclehal.server.cid=2
BOARD_KERNEL_CMDLINE += androidboot.vendor.vehiclehal.server.port=9300
```

Build the trout with `dist` so that it generates the image and host tools in the out/dist folder. Copy image and host tools tarbal to this folder and build the docker image. You may need to rename the image file to match `aosp_trout_x86_64-img.zip` or supply it as a build argument.

## Run

To run the container, start with the following command (replace the tag name). The container takes a minute to start, then you should be able to access the cuttlefish webRTC console at <https://localhost:8443>. As the default container only has the reference apps install which does not contain any map. Any .apk files found in the /root/apk folder when it starts will be automatically installed. See the `-v` flag in the command.

```bash
docker run \
  -d \
  -p 1443:1443 \
  -p 8443:8443 \
  -p 9300:9300 \
  -v $PWD/apks:/root/apks \
  --ulimit nofile=4096:4096 \
  --privileged \
  --name cuttlefish \
  -t <tag-name>
```

The container needs to be started as privileged as it needs access to kvm, vsock and network capabilities.

If you do not want build your own android you could use our pre-built cuttlefish container that has been built with Android Automotive 15.0.0_36 (ap3a)

```bash
docker run \
  -d \
  -p 1443:1443 \
  -p 8443:8443 \
  -p 9300:9300 \
  -v $PWD/apks:/root/apks \
  --ulimit nofile=4096:4096 \
  --privileged \
  --name cuttlefish \
  -t remotivelabs/remotivelabs-cuttlefish
```
