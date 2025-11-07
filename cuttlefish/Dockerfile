FROM us-docker.pkg.dev/android-cuttlefish-artifacts/cuttlefish-orchestration/cuttlefish-orchestration:1.28.0

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
  apt-get install -y less socat unzip netcat-traditional && \
  rm -rf /var/lib/apt/lists/*

ARG IMAGE_FILE_NAME="aosp_trout_x86_64-img.zip"
WORKDIR /root
ADD cvd-host_package.tar.gz .
RUN --mount=type=bind,source=./${IMAGE_FILE_NAME},target=/tmp/${IMAGE_FILE_NAME},readonly \
  unzip /tmp/${IMAGE_FILE_NAME}
COPY init.sh .

ENTRYPOINT [ "/root/init.sh" ]
