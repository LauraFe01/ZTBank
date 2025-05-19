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

// PROVA TEST FUNZIONANTE SQUID by Zazza
1-docker-compose up --build  
2-docker inspect -f "{{.NetworkSettings.IPAddress}}" router (per ottenere l'ip del router)  
3-docker exec -it client-internal (entro dentro il container client-internal)  
4-curl -x http://<IP_PROXY>:3128 http://example.com (faccio la richiesta, IP_PROXY sarebbe l'ip del router)  (per installare curl apt update && apt install -y curl)
5-http://<IP_SPLUNK>:8000 accedo a splunk e vado su Search and Reporting  
6-index=main source="/var/log/squid/access.log (esempio di richiesta)  

// PROVA TEST FUNZIONANTE SNORT by Zazza

1-docker-compose up --build  
2-per generare traffico e testare il monitoraggio del traffico da parte di snort eseguo un ping dal container client-internal verso la rete internal-net del router nel seguente modo:   
   - entro nel container client-internal con: docker exec -it client-internal bash  
   - scarico ping con: apt update && apt install -y iputils-ping (questo è da sistemare, fare in modo che venga scaricato   direttamente)  
   - eseguo il ping con: ping -c 4 192.168.10.254  

dopo aver eseguito il ping andare su splunk all'indirizzo localhost 8000. Su splunk, per verificare le cartelle che vengono monitorate da splunk andare su Impostazioni -> Input dati -> file and directory (li ci saranno alert e snort.log), a quel punto si va su Search and reporting e si immette: source="/var/log/snort/alert" , source="/var/log/snort/snort.log"   

apt-get update && apt-get install netcat-openbsd -y


docker exec -it router bash
ps aux | grep -i flask

