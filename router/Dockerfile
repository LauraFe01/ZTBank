FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Rome

RUN apt-get update && apt-get install -y \
  snort \
  squid \
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
  procps \
  python3 \
  python3-pip \
  python3-dev \
  build-essential \
  pkg-config \
  nano \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Crea directory necessarie per snort e squid
RUN mkdir -p /etc/snort/rules \
    && mkdir -p /var/log/snort/eth0 \
    && mkdir -p /var/log/snort/eth1 \
    && mkdir -p /var/log/snort/eth2 \
    && mkdir -p /var/log/snort/eth3 \
    && mkdir -p /var/log/squid \
    && mkdir -p /var/spool/squid

# Crea le directory necessarie per il meccanismoo di policies
RUN mkdir -p /router/api
RUN mkdir -p /router/api/policies
RUN mkdir -p /router/utils

# Copia files di configurazione di snort e squid
COPY rules/local.rules /etc/snort/rules/
COPY snort_eth0.conf /etc/snort/
COPY snort_eth1.conf /etc/snort/
COPY snort_eth2.conf /etc/snort/
COPY snort_eth3.conf /etc/snort/
COPY squid.conf /etc/squid/

# Copia gli scripts necessari al meccanismo di policies
COPY requirements.txt /router/requirements.txt
COPY api/ /router/api/
#COPY api/app.py /policy-engine/api/app.py
#COPY api/policies/ /policy-engine/api/policies/
COPY utils/ /router/utils/

# Copia il file di avvio
COPY start.sh /usr/local/bin/

# Installa dipendenze Python
RUN pip3 install -r /router/requirements.txt
RUN pip3 install psycopg2-binary

# Gestisce permessi
RUN chmod +x /usr/local/bin/start.sh \
    && chown -R proxy:proxy /var/log/squid \
    && chown -R proxy:proxy /var/spool/squid \
    && chmod 755 /var/log/snort/eth* \
    && chmod 644 /etc/snort/rules/local.rules

# Aggiunge PYTHONPATH
ENV PYTHONPATH="/router:${PYTHONPATH}"

# Crea directory per log del router
RUN mkdir -p /var/log/router && chmod 755 /var/log/router

# Script di avvio
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Comando di avvio del container
CMD ["/start.sh"]
