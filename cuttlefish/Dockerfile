FROM ubuntu:rolling AS runner-base

# Expose Operator Port (HTTP:1080, HTTPS:1443)
EXPOSE 1080 1443
# Expose HO(Host Orchestrator) Port (HTTP:2080, HTTPS:2443)
EXPOSE 2080 2443
# Expose WebRTC Port
EXPOSE 15550-15560
# Expose ADB Port
# Corresponding ADB port for CF instance is, 6520+instance_num-1.
EXPOSE 6520-6620
# to make sure this file always exist
RUN touch /.dockerenv

USER root
WORKDIR /root
RUN set -x
RUN apt update
RUN apt install -y --no-install-recommends \
    ca-certificates \
    curl \
    mesa-utils \
    nginx \
    less \
    socat \
    unzip \
    netcat-traditional \
    sudo \
    mesa-vulkan-drivers \
    mesa-utils-extra \
    vulkan-tools
RUN update-ca-certificates

FROM runner-base AS runner-prod

# android-cuttlefish
# android-cuttlefish-unstable
# android-cuttlefish-nightly
ARG REPO=android-cuttlefish
RUN apt install -y --no-install-recommends gnupg
RUN install -d -m 0755 /etc/apt/keyrings
RUN curl -fsSL https://us-apt.pkg.dev/doc/repo-signing-key.gpg \
    | gpg --dearmor -o /etc/apt/keyrings/android-cuttlefish-archive-keyring.gpg
RUN echo "deb [signed-by=/etc/apt/keyrings/android-cuttlefish-archive-keyring.gpg] https://us-apt.pkg.dev/projects/android-cuttlefish-artifacts $REPO main" \
    | tee -a /etc/apt/sources.list.d/artifact-registry.list
RUN apt update
RUN apt install -y --no-install-recommends \
    cuttlefish-base \
    cuttlefish-user \
    cuttlefish-orchestration


FROM runner-prod AS runner
ARG TARGETARCH

ENV DEBIAN_FRONTEND=noninteractive
ENV EGL_PLATFORM=surfaceless

WORKDIR /root
ADD ${TARGETARCH}/cvd-host_package.tar.gz .
RUN --mount=type=bind,source=./${TARGETARCH}/,target=/tmp/${TARGETARCH}/,readonly \
  unzip /tmp/${TARGETARCH}/aosp_trout_*-img.zip
COPY init.sh .

# TODO(b/491256959): Seek better option than introducing wrapper of bsdtar.
# Add bsdtar wrapper, to avoid owner user/group issue when fetching artifacts.
RUN dpkg-divert --add --rename --divert /usr/bin/bsdtar.real /usr/bin/bsdtar && \
    echo '#!/bin/bash' > /usr/bin/bsdtar && \
    echo '/usr/bin/bsdtar.real --no-same-owner "$@"' >> /usr/bin/bsdtar && \
    chmod +x /usr/bin/bsdtar

RUN usermod -aG kvm root
RUN usermod -aG cvdnetwork root

ENTRYPOINT [ "/root/init.sh" ]
