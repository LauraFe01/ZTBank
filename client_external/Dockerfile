FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    curl \
    iputils-ping \
    iproute2 \
    netcat
   
# Copia lo script di avvio nel container
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY attack.sh /attack.sh
RUN chmod +x /attack.sh

# Imposta lo script come entrypoint
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]