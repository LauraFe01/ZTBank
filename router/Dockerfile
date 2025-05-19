FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
  iptables \
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
  && apt-get clean

# Installa il modulo requests con pip
RUN pip3 install requests
RUN pip3 install flask

# Copia la configurazione di Squid e Snort e lo script di avvio
COPY squid.conf /etc/squid/squid.conf
COPY start.sh /start.sh
RUN chmod +x /start.sh
COPY snort.conf /etc/snort/snort.conf
COPY rules /etc/snort/rules
COPY api/app.py /router/api/app.py



# Crea e configura le directory di cache/log di Squid
RUN mkdir -p /var/spool/squid /var/log/squid && \
    chown -R proxy:proxy /var/spool/squid /var/log/squid && \
    chmod 755 /var/spool/squid /var/log/squid

# Crea e configura la directory di log di Snort
RUN mkdir -p /var/log/snort && chmod 755 /var/log/snort

# Comando di avvio del container
CMD ["/start.sh"]
