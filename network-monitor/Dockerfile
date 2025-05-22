FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# ho lasciato tutto ciò che scaricavo sul container router ma non sarà necessario tutto
# da capire ciò che non serve e cioò che serve
RUN apt-get update && apt-get install -y \
  iptables \
  libiptc0 \
  libnetfilter-queue1 \
  libnetfilter-queue-dev \
  iproute2 \
  tcpdump \
  net-tools \
  iputils-ping \
  curl \
  rsyslog \
  vim \
  squid \
  snort \
  procps \
  python3 \
  python3-pip \
  python3-dev \
  build-essential \
  pkg-config \
  && apt-get clean

# Copia le configurazioni di squid e snort
COPY squid.conf /etc/squid/squid.conf
COPY snort.conf /etc/snort/snort.conf
COPY rules /etc/snort/rules

# Script di avvio
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Crea e configura le directory di cache/log di Squid
RUN mkdir -p /var/spool/squid /var/log/squid && \
    chown -R proxy:proxy /var/spool/squid /var/log/squid && \
    chmod 755 /var/spool/squid /var/log/squid

# Crea e configura la directory di log di Snort
RUN mkdir -p /var/log/snort /var/log/snort/eth0 /var/log/snort/eth1 && \
    chmod 755 /var/log/snort /var/log/snort/eth0 /var/log/snort/eth1

CMD ["/start.sh"]
