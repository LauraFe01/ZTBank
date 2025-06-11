# Zero-Trust Cybersecurity Project

<div align="center">
  <br/>
  <img src="./img/Logo.jpg" width="300" />
  <br/>
  <br/>
  <p>
    Progetto del corso di Advanced-CyberSecurity 2024/2025 <br/>
    Realizzazione di un architettura Zero Trust
  </p>
  <br/>
  <p>
  <a href="#overview"><strong>Overview</strong></a> ·
  <a href="#complete-project-structure"><strong>Complete Project Structure</strong></a> ·
  <a href="#come-buildare-e-avviare"><strong>Come Buildare e Avviare</strong></a> ·
  <a href="#verifica-ssl-e-interazioni-pep"><strong>Verifica SSL e Interazioni PEP</strong></a> ·
  <a href="#esecuzione-use-cases"><strong>Esecuzione Use Cases</strong></a> ·
  <a href="#account-types"><strong>Account Types</strong></a> ·
  <a href="#monitoring-logs-e-splunk"><strong>Monitoring, Logs e Splunk</strong></a> ·
  <a href="#contributing"><strong>Contributing</strong></a> .
 <p><strong>Tecnologie utilizzate: </strong></p>
  <br/>
  <p>
    <a href="https://www.docker.com/">
      <img src="https://img.shields.io/badge/Docker-009edc"/>
    </a>
    <a href="https://www.postgresql.org/">
      <img src="https://img.shields.io/badge/PostgreSQL-009edc"/>
    </a>
    <a href="https://www.netfilter.org/projects/iptables/index.html">
      <img src="https://img.shields.io/badge/iptables-009edc"/>
    </a>
    <a href="https://www.squid-cache.org/">
      <img src="https://img.shields.io/badge/squid-009edc"/>
    </a>
    <a href="https://www.snort.org/">
      <img src="https://img.shields.io/badge/snort-009edc"/>
    </a>
    <a href="https://www.splunk.com/">
      <img src="https://img.shields.io/badge/splunk-009edc"/>
    </a>
  </p>
</div>

## [🚀 Overview](#overview)
Questo progetto implementa un'architettura di sicurezza informatica basata sul modello Zero-Trust. Utilizza servizi containerizzati e best practice di sicurezza per proteggere dati critici e operazioni di rete da accessi non autorizzati.

**Team Members:**

- [Luca Bellante](https://github.com/lucabellantee)
- [Giansimone Coccia](https://github.com/Giansimone-Coccia)
- [Laura Ferretti](https://github.com/LauraFe01)
- [Federico Staffolani](https://github.com/fedeStaffo)
- [Micol Zazzarini](https://github.com/MicolZazzarini)

---

## [📁 Complete Project Structure](#complete-project-structure)

```bash
.
├── client_external/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── uc.sh
├── client_internal/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── uc.sh
├── client_wifi/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── uc.sh
├── db/
│   ├── certs/
│   │   ├── server.crt
│   │   └── server.key
│   ├── init/
│   │   └── 03_ssl.sh
│   ├── data.sql
│   └── schema.sql
├── gateway/
│   ├── Dockerfile
│   ├── apply_blacklist.sh
│   ├── entrypoint.sh
│   ├── local.rules
│   ├── policy.yaml
│   ├── requirements.txt
│   ├── rules.sh
│   ├── snort.conf
│   └── squid.conf
├── logs/
│   ├── policy-engine/
│   ├── router/
│   ├── snort/
│   │   └── logs (snort.log files)
│   └── squid/
│       ├── access.log
│       └── cache.log
├── pdp/
│   ├── data/
│   │   ├── blacklist/
│   │   │   └── blacklist.txt
│   │   ├── GeoLite2-Country.mmdb
│   │   └── trust_db.json
│   ├── .env
│   ├── Dockerfile
│   ├── encrypt_existing.py
│   ├── entrypoint.sh
│   ├── pdp.py
│   ├── policies.py
│   └── utils.py
├── pep/
│   ├── db_scripts/
│   │   ├── db_DAO.py
│   │   ├── db_exec.py
│   │   ├── db_operations.py
│   │   └── __init__.py
│   ├── .env
│   ├── create_users.py
│   ├── Dockerfile
│   ├── pep.py
│   ├── users_db.json      
│   └── user_auth.py
└── splunk-apps/
    ├── dashboard/
    │   └── default/
    │       ├── data/
    │       │   └── ui/
    │       │       ├── nav/default.xml
    │       │       └── views/
    │       │           ├── snort_attack_dashboard.xml
    │       │           └── squid_traffic_dashboard.xml
    │       └── metadata/default.meta
    ├── log_inputs/
    │   ├── local/
    │   │   ├── app.conf
    │   │   ├── inputs.conf
    │   │   ├── props.conf
    │   │   └── savedsearches.conf
    │   └── metadata/local.meta
    └── lookups/
        ├── geo_attr_countries.csv
        ├── geo_attr_us_states.csv
        ├── geo_countries.kmz
        ├── geo_us_states.kmz
        ├── known_clients.csv
        └── README
```

---

## [🔧 Come Buildare e Avviare](#come-buildare-e-avviare)

1. **Assicurarsi di essere nella directory root del progetto**
2. **Verificare che i file **``** usino line endings Unix (**``**)**
   ```bash
   find . -type f -name "*.sh" -exec sed -i 's/\r$//' {} +
   ```
3. **Creare file **``** nella root con i seguenti contenuti:**
   ```dotenv
   POSTGRES_USER=<insert user>
   POSTGRES_PASSWORD=<insert password>
   POSTGRES_DB=<insert name db>
   SPLUNK_PASSWORD=<insert password>
   ```
4. **Avviare tutti i container con build**
   ```bash
   docker compose up --build -d
   ```
5. **Verificare lo stato dei servizi**
   ```bash
   docker compose ps
   ```
6. **Fermare ed eliminare i container, network e volumi**
   ```bash
   docker compose down -v
   ```

---

## [🔐 Verifica SSL e Interazioni PEP](#verifica-ssl-e-interazioni-pep)

1. **Controllare che PostgreSQL accetti connessioni SSL**
   ```bash
   docker exec -it db bash
   psql "sslmode=require host=localhost dbname=bankDB user=user password=cyber_pwd"
   ```
2. **Esempi di richieste al PEP via **``
   - **Login**:

     ```bash
     curl -X POST http://172.24.0.3:3100/login \
       -H "Content-Type: application/json" \
       -c cookies.txt \
       -d '{"username": "giovanni.rossi", "password": "pass_direttore"}'
     ```

   - **Operazione di lettura**:

     ```bash
     curl -X POST http://172.24.0.3:3100/request \
       -H "Content-Type: application/json" \
       -b cookies.txt \
       -d '{"operation": "read", "document_type": "Dati Transazionali", "doc_id": 1}'
     ```

   - **Operazione di scrittura**:

     ```bash
     curl -X POST http://172.24.0.3:3100/request \
       -H "Content-Type: application/json" \
       -b cookies.txt \
       -d '{
         "operation": "write",
         "document_type": "Dati Transazionali",
         "nome_file": "fattura_123.pdf",
         "contenuto": "Contenuto della fattura...",
         "sensibilita": "sensibile"
       }'
     ```

   - **Operazione di cancellazione**:

     ```bash
     curl -X POST http://172.24.0.3:3100/request \
       -H "Content-Type: application/json" \
       -b cookies.txt \
       -d '{"operation": "delete", "document_type": "Dati Transazionali", "doc_id": 2}'
     ```

---

## [⚙️ Esecuzione Use Cases](#esecuzione-use-cases)

Per eseguire gli script di use case (`uc.sh`) all’interno dei container:

```bash
docker exec -it <nome_servizio> bash ./uc.sh
```

Esempio:

```bash
docker exec -it client_internal bash ./uc.sh
```

---

## [🔑 Account Types](#account-types)

I tipi di account sono:

```json
{
  "accounts": [
    { "username": "giovanni.rossi", "role": "Direttore", "password": "pass_direttore" },
    { "username": "marco.bianchi", "role": "Cassiere", "password": "pass_cassiere" },
    { "username": "luca.verdi", "role": "Consulente", "password": "pass_consulente" },
    { "username": "maria.neri", "role": "Cliente", "password": "pass_cliente" },
  ]
}
```

Modificare o aggiungere nuovi tipi di account tramite lo script `pep/create_users.py`.

---

## [📊 Monitoring, Logs e Splunk](#monitoring-logs-e-splunk)

I log sono raccolti in `logs/` e mostrano:

- **Policy Engine**: `logs/policy-engine`
- **Router**: `logs/router`
- **Snort**: `logs/snort`
- **Squid**: `logs/squid`

Dopo aver avviato i container, aprire nel browser:

```
http://localhost:8000/
```

per accedere a Splunk e visualizzare le dashboard personalizzate. Il nome utente è: "**admin**", mentre la password è quella che viene inserita nel file **.env**, presente nella sezione [🔧 Come Buildare e Avviare](#-come-buildare-e-avviare).

### Dashboards 

1. **Snort Attack Dashboard**

   - Visualizza in tempo reale gli alert IDS generati da Snort.
   - Grafico temporale dei rilevamenti per evidenziare picchi di attacco.
   - Top signature alert più frequenti.
   - Classifica IP sorgenti più attivi.
   - Contatori riassuntivi di alert totali e severità.

2. **Squid Traffic Monitoring Dashboard**

   - Trend orario delle richieste proxy negli ultimi 30 giorni.
   - Top 10 URL più richiesti con percentuale di traffico.
   - Top 10 IP client più attivi.
   - Indicatori numerici di richieste totali e URL unici nelle ultime 24h.
   - Distribuzione dei metodi HTTP (GET, POST, ecc.).

---

## [🤝 Contributing](#contributing)

Apri issue, discussion o pull request per suggerimenti e miglioramenti!

