FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Rome

RUN apt-get update && apt-get install -y \
  snort \
  squid \
  iptables \
  libiptc0 \
  iproute2 \
  tcpdump \
  net-tools \
  iputils-ping \
  curl \
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
RUN mkdir -p /var/log/snort \
    && mkdir -p /var/log/squid \
    && mkdir -p /etc/snort/rules \
    && mkdir -p /var/log/snort/eth0 \
    && mkdir -p /var/log/snort/eth1 \
    && mkdir -p /var/log/snort/eth2 \
    && mkdir -p /var/log/snort/eth3 \
    && mkdir -p /var/spool/squid


# Crea le directory necessarie per il meccanismoo di policies
RUN mkdir -p /router/api
RUN mkdir -p /router/utils

# Crea directory per log del router
RUN mkdir -p /var/log/router && chmod 755 /var/log/router

# Copia files di configurazione di snort e squid
COPY rules/local.rules /etc/snort/rules/local.rules
COPY snort_eth0.conf /etc/snort/
COPY snort_eth1.conf /etc/snort/
COPY snort_eth2.conf /etc/snort/
COPY snort_eth3.conf /etc/snort/
COPY squid.conf /etc/squid/

# Copia gli scripts necessari al meccanismo di policies
COPY requirements.txt /router/requirements.txt
COPY api/ /router/api/
COPY api/app.py /router/api/app.py
COPY api/policies/ /router/api/policies/
COPY utils/ /router/utils/

# Installa dipendenze Python
RUN pip3 install -r /router/requirements.txt
RUN pip3 install psycopg2-binary

RUN groupadd -r squid && useradd -r -g squid squid \
    && chown -R proxy:proxy /var/log/squid \
    && chown -R proxy:proxy /var/spool/squid \
    && chmod 755 /var/log/snort \
    && chmod 755 /var/log/snort/eth0 \
    && chmod 755 /var/log/snort/eth1 \
    && chmod 755 /var/log/snort/eth2 \
    && chmod 755 /var/log/snort/eth3 \
    && chmod 644 /etc/snort/rules/local.rules \
    && chmod -R 777 /var/log/snort


# Aggiunge PYTHONPATH
ENV PYTHONPATH="/router:${PYTHONPATH}"

# file di avvio
COPY start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh
CMD ["/usr/local/bin/start.sh"]
