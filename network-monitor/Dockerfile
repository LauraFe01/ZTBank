FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Rome

# Installa pacchetti necessari
RUN apt-get update && apt-get install -y \
    snort \
    squid \
    rsyslog \
    net-tools \
    tcpdump \
    iptables \
    iputils-ping \
    nano \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crea directory necessarie
RUN mkdir -p /etc/snort/rules \
    && mkdir -p /var/log/snort/eth0 \
    && mkdir -p /var/log/snort/eth1 \
    && mkdir -p /var/log/snort/eth2 \
    && mkdir -p /var/log/snort/eth3 \
    && mkdir -p /var/log/squid \
    && mkdir -p /var/spool/squid

# Copia file di configurazione
COPY rules/local.rules /etc/snort/rules/
COPY snort_eth0.conf /etc/snort/
COPY snort_eth1.conf /etc/snort/
COPY snort_eth2.conf /etc/snort/
COPY snort_eth3.conf /etc/snort/
COPY squid.conf /etc/squid/
COPY start.sh /usr/local/bin/

RUN chmod +x /usr/local/bin/start.sh \
    && chown -R proxy:proxy /var/log/squid \
    && chown -R proxy:proxy /var/spool/squid \
    && chmod 755 /var/log/snort/eth* \
    && chmod 644 /etc/snort/rules/local.rules

# Espone porte
EXPOSE 3128

# Avvia lo script
CMD ["/usr/local/bin/start.sh"]
