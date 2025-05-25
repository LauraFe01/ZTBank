# client-external/Dockerfile
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
        iproute2 \
        curl \
        iputils-ping \
        net-tools \
        netcat \
        traceroute \
        postgresql-client \
    && apt-get clean

# Script di test
COPY test_connection.sh /usr/local/bin/test_connection.sh
RUN chmod +x /usr/local/bin/test_connection.sh

# Script per aggiungere rotte
COPY setup_routes.sh /usr/local/bin/setup_routes.sh
RUN chmod +x /usr/local/bin/setup_routes.sh


# Usa lo script di inizializzazione come entrypoint
CMD ["bash"]