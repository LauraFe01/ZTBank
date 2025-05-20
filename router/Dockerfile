FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

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

# Copia requirements e installa dipendenze Python
COPY api/requirements.txt /router/api/requirements.txt
RUN pip3 install -r /router/api/requirements.txt

# Copia la configurazione di Squid e Snort e lo script di avvio
COPY squid.conf /etc/squid/squid.conf
COPY start.sh /start.sh
RUN chmod +x /start.sh
COPY snort.conf /etc/snort/snort.conf
COPY rules /etc/snort/rules
COPY api/app.py /router/api/app.py
# Aggiungi questa riga dopo COPY api/app.py /router/api/app.py
COPY api/test_webhook.py /router/api/test_webhook.py
COPY api/generate_portscan.py /router/api/generate_portscan.py
COPY api/monitor_policy.py /router/api/monitor_policy.py

# Crea e configura le directory di cache/log di Squid
RUN mkdir -p /var/spool/squid /var/log/squid && \
    chown -R proxy:proxy /var/spool/squid /var/log/squid && \
    chmod 755 /var/spool/squid /var/log/squid

# Crea e configura la directory di log di Snort
RUN mkdir -p /var/log/snort /var/log/snort/eth0 /var/log/snort/eth1 && \
    chmod 755 /var/log/snort /var/log/snort/eth0 /var/log/snort/eth1

# Crea directory per log del router
RUN mkdir -p /var/log/router && chmod 755 /var/log/router

# Comando di avvio del container
CMD ["/start.sh"]


