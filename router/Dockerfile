FROM debian:bullseye

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
  procps \
  && apt-get clean

COPY squid.conf /etc/squid/squid.conf
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Assicurati che le directory cache e log esistano con i permessi corretti
RUN mkdir -p /var/spool/squid /var/log/squid && \
    chown -R proxy:proxy /var/spool/squid /var/log/squid && \
    chmod 755 /var/spool/squid /var/log/squid

CMD ["/start.sh"]