FROM ubuntu:22.04

# Installazione strumenti base e per generare traffico
RUN apt-get update && apt-get install -y \
    iproute2 \
    iputils-ping \
    bash \
    curl \
    netcat \
    telnet \
    postgresql-client \
    && apt-get clean

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
