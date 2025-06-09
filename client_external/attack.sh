#!/bin/bash

# IP e porta del PEP sulla rete zt-gateway
docker_net="172.24.0.3"
PEP_IP="$docker_net"
PEP_PORT=3100
COOKIE_FILE="cookies.txt"

# Controllo dipendenza jq per formattazione JSON
echo "=== Verifica presenza di jq ==="
if ! command -v jq >/dev/null; then
  echo "ATTENZIONE: 'jq' non è installato. Gli output JSON non verranno formattati." >&2
  JQ_CMD="cat"
else
  echo "jq trovato. I risultati JSON verranno formattati." >&2
  JQ_CMD="jq"
fi

# Funzione per selezione document_type
doc_type_select() {
  echo "Seleziona il tipo di documento:"
  echo "1) Dati Transazionali"
  echo "2) Dati Personali"
  echo "3) Altro"
  read -p "Scelta: " dt_choice
  case $dt_choice in
    1) DOCUMENT_TYPE="Dati Transazionali" ;;
    2) DOCUMENT_TYPE="Dati Personali" ;;
    3) read -p "Inserisci tipo di documento: " DOCUMENT_TYPE ;;
    *) echo "Scelta non valida, impostato default Dati Transazionali"; DOCUMENT_TYPE="Dati Transazionali" ;;
  esac
}

# Funzione per selezione sensibilita
group_select() {
  echo "Seleziona livello di sensibilita':"
  echo "1) sensibile"
  echo "2) non_sensibile"
  read -p "Scelta: " s_choice
  case $s_choice in
    1) SENSITIVITY="sensibile" ;;
    2) SENSITIVITY="non_sensibile" ;;
    *) echo "Scelta non valida, impostato default non_sensibile"; SENSITIVITY="non_sensibile" ;;
  esac
}

# Funzione per il login
login() {
  echo "=== Login utente ==="
  read -p "Username: " user
  read -s -p "Password: " pass
  echo
  curl -s -X POST http://$PEP_IP:$PEP_PORT/login \
       -H "Content-Type: application/json" \
       -c $COOKIE_FILE \
       -d "{\"username\": \"$user\", \"password\": \"$pass\"}" \
       | $JQ_CMD
  echo "Login effettuato e cookie salvati in $COOKIE_FILE"
}

# Funzione per il logout
logout() {
  echo "=== Logout utente ==="
  curl -s -X POST http://$PEP_IP:$PEP_PORT/logout \
       -H "Content-Type: application/json" \
       -b $COOKIE_FILE \
       | $JQ_CMD
  rm -f $COOKIE_FILE
  echo "Logout effettuato e cookie rimossi"
}

# Funzione per operazione di lettura (read)
read_op() {
  echo "=== Lettura documento ==="
  doc_type_select
  group_select
  read -p "ID documento: " doc_id
  curl -s -X POST http://$PEP_IP:$PEP_PORT/request \
       -H "Content-Type: application/json" \
       -b $COOKIE_FILE \
       -d "{\"operation\": \"read\", \"document_type\": \"$DOCUMENT_TYPE\", \"doc_id\": $doc_id, \"sensibilita\": \"$SENSITIVITY\"}" \
       | $JQ_CMD
}

# Funzione per operazione di scrittura (write)
write_op() {
  echo "=== Scrittura documento ==="
  doc_type_select
  read -p "Nome file: " file_name
  read -p "Contenuto (testo): " content
  group_select
  curl -s -X POST http://$PEP_IP:$PEP_PORT/request \
       -H "Content-Type: application/json" \
       -b $COOKIE_FILE \
       -d "{\"operation\": \"write\", \"document_type\": \"$DOCUMENT_TYPE\", \"nome_file\": \"$file_name\", \"contenuto\": \"$content\", \"sensibilita\": \"$SENSITIVITY\"}" \
       | $JQ_CMD
}

# Funzione per operazione di cancellazione (delete)
delete_op() {
  echo "=== Cancellazione documento ==="
  doc_type_select
  group_select
  read -p "ID documento da cancellare: " doc_id
  curl -s -X POST http://$PEP_IP:$PEP_PORT/request \
       -H "Content-Type: application/json" \
       -b $COOKIE_FILE \
       -d "{\"operation\": \"delete\", \"document_type\": \"$DOCUMENT_TYPE\", \"doc_id\": $doc_id, \"sensibilita\": \"$SENSITIVITY\"}" \
       | $JQ_CMD
}

# Funzioni di attacco simulate (lecite/informative)
# Funzione per eseguire l'attacco DoS simulato (POST ripetuti)
attacco_1() {
  echo "=== Simulazione attacco DoS autenticato al PEP ==="
  for i in {1..3}; do
    echo "[$i] Invio richiesta POST autenticata a /request"
    curl -s -X POST http://$PEP_IP:$PEP_PORT/request \
         -H "Content-Type: application/json" \
         -b $COOKIE_FILE \
         -d '{"operation": "read", "document_type": "Dati Transazionali", "doc_id": 1}' \
         | $JQ_CMD
  done
  echo "Richieste POST inviate."
}

# Funzione per eseguire il port scanning
attacco_2() {
  echo "=== Port scanning da 3070 a 3120 verso $PEP_IP ==="
  nmap -Pn -sS -p3070-3120 $PEP_IP
  echo "Port scanning completato."
}

# Funzione per inviare il payload MIPS SGI NOOP
attacco_3() {
  echo "=== Invio payload SGI NOOP sled per triggerare la regola Snort ==="
  echo -ne $'\x03\xe0\xf8%\x03\xe0\xf8%\x03\xe0\xf8%\x03\xe0\xf8%' | nc -u -w1 $PEP_IP $PEP_PORT
  echo "Payload inviato!"
}

# Menu interattivo
while true; do
  echo
  echo "=== Menu Operazioni ==="
  echo "1) Login"
  echo "2) Logout"
  echo "3) Read (lettura)"
  echo "4) Write (scrittura)"
  echo "5) Delete (cancellazione)"
  echo "6) Simula DoS"
  echo "7) Port scanning"
  echo "8) Payload NOOP Snort"
  echo "q) Esci"
  echo "========================"
  read -p "Scegli un'opzione: " scelta

  case $scelta in
    1) login ;;
    2) logout ;;
    3) read_op ;;
    4) write_op ;;
    5) delete_op ;;
    6) attacco_1 ;;
    7) attacco_2 ;;
    8) attacco_3 ;;
    q|Q) echo "Uscita dallo script."; break ;;
    *) echo "Opzione non valida. Riprova." ;;
  esac

done
