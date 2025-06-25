FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl \
    iputils-ping \
    iproute2 \
    netcat \
    hping3 \
    nmap \
    snort \
    jq \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY entrypoint.sh /app/entrypoint.sh
COPY uc.sh /app/uc.sh

RUN chmod +x /app/entrypoint.sh /app/uc.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["bash"]
