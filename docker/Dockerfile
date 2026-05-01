FROM ubuntu:24.04

LABEL maintainer="talal.abouhaiba@gmail.com"

ARG TARGETARCH
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        ca-certificates \
        wget \
        tzdata \
    && rm -rf /var/lib/apt/lists/*

# Pull arch-correct litestream + s6-overlay binaries.
# litestream uses arm64/amd64; s6-overlay v2 uses aarch64/amd64.
RUN set -eux; \
    case "${TARGETARCH}" in \
      amd64) LITESTREAM_ARCH=amd64; S6_ARCH=amd64 ;; \
      arm64) LITESTREAM_ARCH=arm64; S6_ARCH=aarch64 ;; \
      *) echo "Unsupported TARGETARCH: ${TARGETARCH}"; exit 1 ;; \
    esac; \
    wget -O /tmp/litestream.tar.gz \
        "https://github.com/benbjohnson/litestream/releases/download/v0.3.8/litestream-v0.3.8-linux-${LITESTREAM_ARCH}-static.tar.gz"; \
    tar -C /usr/local/bin -xzf /tmp/litestream.tar.gz; \
    rm /tmp/litestream.tar.gz; \
    wget -O /tmp/s6-overlay-installer \
        "https://github.com/just-containers/s6-overlay/releases/download/v2.2.0.3/s6-overlay-${S6_ARCH}-installer"; \
    chmod +x /tmp/s6-overlay-installer; \
    /tmp/s6-overlay-installer /; \
    rm /tmp/s6-overlay-installer

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN python3 --version
RUN python3 -m pip install --break-system-packages --no-cache-dir -r requirements.txt

COPY . /app

COPY etc/cont-init.d /etc/cont-init.d
COPY etc/services.d /etc/services.d
COPY etc/litestream.yml /etc/litestream.yml

ENV S6_KILL_GRACETIME=0
ENV S6_SYNC_DISKS=1
ENV S6_BEHAVIOUR_IF_STAGE2_FAILS=2

EXPOSE 9205
ENTRYPOINT [ "/init" ]
