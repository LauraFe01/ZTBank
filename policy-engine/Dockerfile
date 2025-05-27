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
  procps \
  python3 \
  python3-pip \
  python3-dev \
  build-essential \
  pkg-config \
  && apt-get clean

# Copia requirements e installa dipendenze Python
COPY requirements.txt /policy-engine/requirements.txt
RUN pip3 install -r /policy-engine/requirements.txt
RUN pip3 install psycopg2-binary

# FIX: Crea le directory prima del COPY
RUN mkdir -p /policy-engine/api/policies
RUN mkdir -p /policy-engine/utils

# Copia gli scripts nel container
COPY api/app.py /policy-engine/api/app.py
COPY api/policies/ /policy-engine/api/policies/

# FIX: COPY utils con struttura corretta
COPY utils/ /policy-engine/utils/

# FIX: Aggiungi PYTHONPATH
ENV PYTHONPATH="/policy-engine:${PYTHONPATH}"

# Crea directory per log del router
RUN mkdir -p /var/log/policy-engine && chmod 755 /var/log/policy-engine

# Script di avvio
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Comando di avvio del container
CMD ["/start.sh"]



