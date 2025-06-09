FROM ubuntu:22.04

# Evita richieste interattive durante installazioni
ENV DEBIAN_FRONTEND=noninteractive

# Aggiorna e installa gli strumenti di rete
RUN apt-get update && apt-get install -y \
    curl \
    iputils-ping \
    iproute2 \
    netcat \
    hping3 \
    nmap \
    snort \
    jq \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Imposta la working directory
WORKDIR /app

# Copia gli script nel container
COPY entrypoint.sh /app/entrypoint.sh
COPY attack.sh /app/attack.sh

# Rendi gli script eseguibili
RUN chmod +x /app/entrypoint.sh /app/attack.sh

# Imposta lo script di avvio come entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["bash"]
