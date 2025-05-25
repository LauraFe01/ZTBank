FROM ubuntu:22.04

# Aggiorna pacchetti e installa iproute2 (per ip route), iputils-ping (ping), e bash
RUN apt-get update && apt-get install -y iproute2 iputils-ping bash && apt-get clean

# Copia lo script di avvio nel container
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Imposta lo script come entrypoint
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
