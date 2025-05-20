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


// PROVA DI IMPLEMENTAZIONE POLICY CON MECCANISMO WEBHOOK by Zazza

Policy 8.2: Reputazione Storica delle Reti  
"Reti (IP) con più di 10 tentativi di attacco negli ultimi 30 giorni → Riduzione automatica della fiducia di 25-30 punti e blocco preventivo"  
Questa policy prevede:  

1. Monitoraggio dei tentativi di attacco con Snort    
2. Aggregazione dei dati in Splunk  
3. Creazione di una saved search che identifichi IP con più di 10 tentativi di attacco  
4. Attivazione del webhook quando la soglia viene superata  
5. Implementazione della policy nel server Flask con blocco automatico dell'IP  

- su snort.rules: la regola che ci interessa è quella commentata con Port scanning detection

Per generare gli eventi relativi a questa policy, andare sul file local.rules. La rule relativa a questa policy è quella relativa alla "Port scanning detection", trovate li commentate le istruzioni per generare gli eventi. Vi ritroverete poi i log di questi eventi sul file logs/snort/eth0/alert  
  
A questo punto avete i log necessari per far attivare la policy. La search di splunk per ottenere i dati che ci interessano si trova nel file savedsearches.conf (saved search relativa alla policy 8.2). Potete testare la search direttamente dall'interfaccia di splunk utilizzando l'app Search and Reporting.  
  
Sempre sull'interfaccia di splunk, se volete verificare che splunk monitori effettivamente i files di log di squid e snort, andate su -> Impostazioni -> Input Dati -> File and Directory  
  
Se invece volete monitorare gli allarmi delle saved search e la loro struttura in generale, andate su -> Impostazioni -> Ricerche, Report e Allarmi -> Impostate come filtri App: My Custom Alerts, Proprietario: Tutto. Vedrete le saved search configurate e potrete monitorare quanti allarmi vengono inviati e altre informazioni utili.  
  
Per verificare invece i log del meccanismo di webhook potete andare su Impostazioni -> Azioni d'Allarme -> sulla riga relativa a webhook: Visualizza eventi di log.  

Se il webhook è andato a buon fine, significa che effettivamente i dati del payload sono stati inviati al server Flask (per ora solo un server di prova che riceve i dati del payload). Potete verificarli così:
- entrate dentro il container router: docker exec -it router bash
- cat webhook.log

