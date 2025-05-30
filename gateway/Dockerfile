FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    rsyslog \
    iptables \
    squid \
    python3 \
    python3-pip


COPY pep.py /opt/pep.py
COPY rules.sh /opt/rules.sh
COPY requirements.txt /opt/requirements.txt
COPY 10-iptables.conf /etc/rsyslog.d/10-iptables.conf
COPY logs /var/logs

RUN pip install -r /opt/requirements.txt
RUN chmod +x /opt/rules.sh && mkdir -p /var/logs && touch /var/logs/iptables.log && chmod 666 /var/logs/iptables.log

CMD ["/opt/rules.sh"]
