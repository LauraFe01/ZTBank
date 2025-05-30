FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    iptables \
    squid \
    python3 \
    python3-pip


COPY pep.py /opt/pep.py
COPY rules.sh /opt/rules.sh
COPY requirements.txt /opt/requirements.txt
COPY logs /var/logs

RUN pip install -r /opt/requirements.txt
RUN chmod +x /opt/rules.sh && mkdir -p /var/logs

CMD ["/opt/rules.sh"]
