# Verifica di Rete e Connettività

- ping -c 1 192.168.200.10 # per verificare il path via router (test di connettività) (OK TESTATO)
  ICMP Ping to DB detected su eth0
  ICMP Ping detected su eth0
  Ping to DB detected [] [Priority: 0] {ICMP} 192.168.200.254 -> 192.168.200.10 su eth2
  ICMP Ping detected [**] [Priority: 0] {ICMP} 192.168.200.254 -> 192.168.200.10 su eth2
  ICMP Ping detected [**] [Priority: 0] {ICMP} 192.168.200.10 -> 192.168.200.254 su eth2

- traceroute 192.168.200.10  # per confermare il passaggio attraverso il router (OK TESTATO)
  ICMP Ping detected [**] [Priority: 0] {ICMP} 192.168.200.10 -> 192.168.200.254
  ICMP Ping detected [**] [Priority: 0] {ICMP} 192.168.200.10 -> 192.168.200.254
  ICMP Ping detected [**] [Priority: 0] {ICMP} 192.168.200.10 -> 192.168.200.254
  ICMP Ping detected [**] [Priority: 0] {ICMP} 192.168.200.10 -> 192.168.200.254
  ICMP Ping detected [**] [Priority: 0] {ICMP} 192.168.200.10 -> 192.168.200.254
  ICMP Ping detected [**] [Priority: 0] {ICMP} 192.168.200.10 -> 192.168.200.254
  (eth2)

# Diagnostica porte e routing

- ip route # per visualizzare la tabella di routing

- nc -zv 192.168.200.10 5432 # Verifica che la porta del DB (5432) sia aperta (OK TESTATO)
  (non stampa niente)

# Connessione al database PostgreSQL

- psql -h 192.168.200.10 -U myuser -d mydb # connessione al db, alla richiesta della password inserire mypass (OK TESTATO)
  (non stampa niente)

- telnet 192.168.200.10 5432 # connessione TCP generica
  (non stampa niente)
# Curl per simulare richieste HTTP al router


