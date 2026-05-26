FROM us-docker.pkg.dev/android-cuttlefish-artifacts/cuttlefish-orchestration/cuttlefish-orchestration:1.53.0
ARG TARGETARCH

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
  apt-get install -y less socat unzip netcat-traditional && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /root
ADD ${TARGETARCH}/cvd-host_package.tar.gz .
RUN --mount=type=bind,source=./${TARGETARCH}/,target=/tmp/${TARGETARCH}/,readonly \
  unzip /tmp/${TARGETARCH}/aosp_trout_*-img.zip
COPY init.sh .

ENTRYPOINT [ "/root/init.sh" ]
