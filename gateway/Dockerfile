FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Installazione pacchetti essenziali in un solo layer, con pulizia cache per ridurre dimensioni immagine
RUN apt-get update && apt-get install -y \
    iptables \
    squid \
    snort \
    python3 \
    python3-pip \
    net-tools \
    tshark \
    tcpdump \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


#################
##   SQUID     ##
#################

# 1) Creiamo le directory necessarie per Squid
RUN mkdir -p /var/log/squid \
    && mkdir -p /var/spool/squid \
    && chown -R proxy:proxy /var/log/squid /var/spool/squid

# 2) Copiamo il nostro file squid.conf custom
COPY squid.conf /etc/squid/squid.conf


#################
##   SNORT     ##
#################

# 1) Creiamo la directory necessarie per Snort
RUN mkdir -p /var/log/snort \
    && mkdir -p /etc/snort/rules 

# 2) Copiamo i nostri file snort.conf e local.rules
COPY local.rules /etc/snort/rules/local.rules
COPY snort.conf /etc/snort/


##########################
##  SCRIPT E DEPENDENCY ##
##########################

# (il resto rimane invariato)
COPY rules.sh /opt/rules.sh
COPY requirements.txt /opt/requirements.txt

RUN pip install -r /opt/requirements.txt
RUN chmod +x /opt/rules.sh && mkdir -p /var/logs

COPY entrypoint.sh /opt/entrypoint.sh
RUN chmod +x /opt/entrypoint.sh

ENTRYPOINT ["/opt/entrypoint.sh"]