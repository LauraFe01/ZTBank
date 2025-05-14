# AdvCybersecProj

docker system prune // Pulisce il sistema 
docker network create --driver=bridge --subnet=192.168.200.0/24 net-lab  // Lascia perdere 

docker network inspect advcybersecproj_net-lab  // Se si vuole avere più info sulla rete

docker-compose up --build -d // Avvio di tutti i container


docker exec -it router bash // Si entra dentro il container router
docker exec -it snort /bin/sh // Si entra dentro il container snort
docker exec -it splunk bash // Si entra dentro il container splunk
http://localhost:8000/  // Si entra nella Dashboard di splunk
docker exec -it cient /bin/sh // Si entra dentro il container client

// Prove per vedere se tutto è ok
ping 192.168.200.11
curl -i http://192.168.200.11:5432

// Attivo il logging da iptables
iptables -A OUTPUT -j LOG --log-prefix "OUT_TRAFFIC: "

// Rende accessibile il file starts.sh
chmod +x router/start.sh
