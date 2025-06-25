FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    iptables \
    squid \
    snort \
    python3 \
    python3-pip \
    net-tools \
    inotify-tools \
    curl \
    tshark \
    tcpdump \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# SQUID
RUN mkdir -p /var/log/squid \
    && mkdir -p /var/spool/squid \
    && chown -R proxy:proxy /var/log/squid /var/spool/squid

COPY squid.conf /etc/squid/squid.conf

COPY apply_blacklist.sh /opt/apply_blacklist.sh
RUN chmod +x /opt/apply_blacklist.sh

# SNORT
RUN mkdir -p /var/log/snort \
    && mkdir -p /etc/snort/rules 

COPY local.rules /etc/snort/rules/local.rules
COPY snort.conf /etc/snort/

# IPTABLES
COPY rules.sh /opt/rules.sh
RUN chmod +x /opt/rules.sh && mkdir -p /var/logs

# REQUIREMENTS
COPY requirements.txt /opt/requirements.txt
RUN pip install -r /opt/requirements.txt

# ENTRYPOINT
COPY entrypoint.sh /opt/entrypoint.sh
RUN chmod +x /opt/entrypoint.sh
ENTRYPOINT ["/opt/entrypoint.sh"]