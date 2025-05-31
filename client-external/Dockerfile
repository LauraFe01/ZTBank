FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    iputils-ping \
    iproute2 \
    net-tools \
    curl \
    dnsutils \
    telnet \
    tcpdump \
    traceroute \
    netcat \
    postgresql-client \
    vim \
    nano \
    less \
    procps \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia lo script di avvio nel container
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Imposta lo script come entrypoint
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
