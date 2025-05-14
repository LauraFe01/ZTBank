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
  && apt-get clean

COPY squid.conf /etc/squid/squid.conf
COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
