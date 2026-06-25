#!/usr/bin/env bash
# Fetch Cuttlefish build artifacts from the Android builder VM and build the
# Docker image.
#
# Usage:
#   ./build.sh [-a arch] [-i instance] [-z zone] [-u user] [-r remote-dir] [-t tag] [-s]
#
#   -a  Target arch / artifact folder: amd64 (default) or arm64
#   -i  GCE instance name              (default: android-builder-vm)
#   -z  GCE zone                       (default: europe-west1-d)
#   -u  Remote SSH user                (default: ubuntu)
#   -r  Remote dist dir on the VM      (default: depends on arch)
#   -t  Docker image tag               (default: apa:3)
#   -s  Skip the download, just build from existing local artifacts
set -euo pipefail

ARCH=amd64
INSTANCE=android-builder-vm
ZONE=europe-west1-d
USER=ubuntu
REMOTE_DIR=
TAG=apa:4
SKIP_DOWNLOAD=false

while getopts "a:i:z:u:r:t:sh" opt; do
  case "$opt" in
    a) ARCH=$OPTARG ;;
    i) INSTANCE=$OPTARG ;;
    z) ZONE=$OPTARG ;;
    u) USER=$OPTARG ;;
    r) REMOTE_DIR=$OPTARG ;;
    t) TAG=$OPTARG ;;
    s) SKIP_DOWNLOAD=true ;;
    h) sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "Try '$0 -h' for usage." >&2; exit 2 ;;
  esac
done

cd "$(dirname "$0")"

# Default remote dist dir depends on the target board.
if [ -z "$REMOTE_DIR" ]; then
  case "$ARCH" in
    amd64) REMOTE_DIR="~/git/google/android/out/trout_x86/dist" ;;
    arm64) REMOTE_DIR="~/git/google/android/out/trout_arm64/dist" ;;
    *) echo "Unknown arch '$ARCH' — pass -r to set the remote dist dir." >&2; exit 2 ;;
  esac
fi

mkdir -p "$ARCH"

if [ "$SKIP_DOWNLOAD" = false ]; then
  echo ">> Fetching artifacts from $USER@$INSTANCE ($ZONE) into $ARCH/ ..."
  gcloud compute scp --zone="$ZONE" \
    "$USER@$INSTANCE:$REMOTE_DIR/aosp_trout_*-img-ubuntu.zip" \
    "$ARCH/aosp_trout_$([ "$ARCH" = amd64 ] && echo x86_64 || echo arm64)-img.zip"
  gcloud compute scp --zone="$ZONE" \
    "$USER@$INSTANCE:$REMOTE_DIR/cvd-host_package.tar.gz" \
    "$ARCH/cvd-host_package.tar.gz"
else
  echo ">> Skipping download, using existing artifacts in $ARCH/"
fi

# Sanity-check the artifacts exist before building.
shopt -s nullglob
imgs=("$ARCH"/aosp_trout_*-img.zip)
if [ ${#imgs[@]} -eq 0 ] || [ ! -f "$ARCH/cvd-host_package.tar.gz" ]; then
  echo "Missing build artifacts in $ARCH/ — expected aosp_trout_*-img.zip and cvd-host_package.tar.gz." >&2
  exit 1
fi

echo ">> Building Docker image $TAG ..."
docker build . -t "$TAG"

echo ">> Done. Built $TAG"
