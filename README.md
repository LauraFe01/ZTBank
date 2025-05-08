# AdvCybersecProj

Mega pulizia di docker(elimina TUTTO): docker system prune
docker network create --driver=bridge --subnet=192.168.200.0/24 net-lab

Se si vuole avere più info sulla rete: docker network inspect advcybersecproj_net-lab

docker-compose up --build -d

docker exec -it router bash
ping 192.168.200.11
curl -i http://192.168.200.11:5432

iptables -A OUTPUT -j LOG --log-prefix "OUT_TRAFFIC: "
