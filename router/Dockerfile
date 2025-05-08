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
  && apt-get clean

# Copia uno script di avvio personalizzato
COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
