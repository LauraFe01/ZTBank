# AdvCybersecProj

docker network create --driver=bridge --subnet=192.168.100.0/24 net-lab

docker-compose up --build -d

docker exec -it router bash
ping 192.168.200.11
curl -i http://192.168.200.11:5432

iptables -A OUTPUT -j LOG --log-prefix "OUT_TRAFFIC: "
