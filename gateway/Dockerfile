FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    iptables \
    squid \
    python3 \
    python3-pip \
    net-tools

# 1) Creiamo le directory necessarie per Squid
RUN mkdir -p /var/log/squid \
    && mkdir -p /var/spool/squid \
    && chown -R proxy:proxy /var/log/squid /var/spool/squid

# 2) Copiamo il nostro file squid.conf custom
COPY squid.conf /etc/squid/squid.conf

# (il resto rimane invariato)
COPY rules.sh /opt/rules.sh
COPY requirements.txt /opt/requirements.txt

RUN pip install -r /opt/requirements.txt
RUN chmod +x /opt/rules.sh && mkdir -p /var/logs

COPY entrypoint.sh /opt/entrypoint.sh
RUN chmod +x /opt/entrypoint.sh

ENTRYPOINT ["/opt/entrypoint.sh"]
