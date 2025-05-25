    # Database Schema - Sistema Zero Trust Bancario

## Panoramica

Questo database supporta un sistema di **architettura Zero Trust** per un ambiente bancario, implementando controlli di accesso basati su trust score, gestione utenti con ruoli specifici, e monitoraggio automatico della sicurezza di rete.

## Diagramma Entità-Relazione

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│     UTENTI      │◄────►│   UTENTI_IP      │      │ FILE_DOCUMENTI  │
├─────────────────┤      ├──────────────────┤      ├─────────────────┤
│ id (PK)         │      │ id (PK)          │      │ id (PK)         │
│ username        │      │ utente_id (FK)   │      │ nome_file       │
│ ruolo           │      │ ip_address       │      │ contenuto       │
│ codice_fiscale  │      │ ip_ruolo         │      │ sensibilita     │
│ indirizzo       │      └──────────────────┘      │ proprietario_id │
│ email           │                                 └─────────────────┘
│ telefono        │                                          │
│ trust_score     │                                          │
└─────────────────┘                                          │
         │                                                   │
         │                                                   │
         │               ┌─────────────────┐                 │
         └──────────────►│   ACCESS_LOG    │◄────────────────┘
                         ├─────────────────┤
                         │ id (PK)         │
                         │ utente_id (FK)  │
                         │ file_id (FK)    │
                         │ azione          │
                         │ timestamp       │
                         │ esito           │
                         │ motivazione     │
                         └─────────────────┘

┌─────────────────────┐      ┌──────────────────────┐
│   NETWORK_TRUST     │      │ TRUST_REDUCTION_LOG  │
├─────────────────────┤      ├──────────────────────┤
│ id (PK)             │◄────►│ id (PK)              │
│ ip_address (UNIQUE) │      │ ip_address           │
│ initial_trust_score │      │ reduction_amount     │
│ current_trust_score │      │ reason               │
│ attack_count        │      │ attack_count         │
│ last_attack_time    │      │ timestamp            │
│ last_update         │      │ applied_by           │
│ is_blocked          │      └──────────────────────┘
│ notes               │
└─────────────────────┘
```

## Dettaglio Tabelle

### UTENTI
Memorizza informazioni sui soggetti del sistema bancario con i loro rispettivi trust score.

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| **id** | SERIAL PRIMARY KEY | Identificatore univoco |
| **username** | TEXT UNIQUE NOT NULL | Nome utente univoco |
| **ruolo** | ENUM | Enum ('direttore', 'cassiere', 'consulente', 'cliente') |
| **codice_fiscale** | TEXT UNIQUE NOT NULL | Codice fiscale univoco |
| **indirizzo** | TEXT | Indirizzo di residenza |
| **email** | TEXT | Email |
| **telefono** | TEXT | Numero di telefono |
| **trust_score** | INTEGER | Punteggio di fiducia base (0-100) |

### UTENTI_IP
Associa gli utenti ai loro indirizzi IP e definisce il tipo di rete utilizzato.

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| **id** | SERIAL PRIMARY KEY | Identificatore univoco |
| **utente_id** | INTEGER FK | Riferimento a UTENTI |
| **ip_address** | INET NOT NULL | Indirizzo IP |
| **ip_ruolo** | ENUM | Enum ('internal', 'external', 'wifi') |

**Vincoli**: UNIQUE(utente_id, ip_address)

### FILE_DOCUMENTI
Gestisce le risorse del sistema bancario con diversi livelli di sensibilità.

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| **id** | SERIAL PRIMARY KEY | Identificatore univoco |
| **nome_file** | TEXT NOT NULL | Nome del file |
| **contenuto** | TEXT | Contenuto del file |
| **sensibilita** | ENUM | Enum ('sensibile', 'non_sensibile') |
| **proprietario_id** | INTEGER FK | Riferimento a UTENTI |

### ACCESS_LOG
Traccia tutti i tentativi di accesso alle risorse del sistema.

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| **id** | SERIAL PRIMARY KEY | Identificatore univoco |
| **utente_id** | INTEGER FK | Riferimento a UTENTI |
| **file_id** | INTEGER FK | Riferimento a FILE_DOCUMENTI |
| **azione** | ENUM | Enum ('lettura', 'scrittura', 'cancellazione') |
| **timestamp** | TIMESTAMP | Timestamp dell'operazione (DEFAULT CURRENT_TIMESTAMP) |
| **esito** | BOOLEAN NOT NULL | Risultato dell'operazione |
| **motivazione** | TEXT | Motivo dell'operazione |

### NETWORK_TRUST (Policy 1)
Implementa il sistema di fiducia dinamica per gli indirizzi IP della rete.

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| **id** | SERIAL PRIMARY KEY | Identificatore univoco |
| **ip_address** | INET NOT NULL UNIQUE | Indirizzo IP |
| **initial_trust_score** | INTEGER DEFAULT 100 | Punteggio iniziale (0-100) |
| **current_trust_score** | INTEGER DEFAULT 100 | Punteggio attuale (0-100) |
| **attack_count** | INTEGER DEFAULT 0 | Numero di attacchi rilevati |
| **last_attack_time** | TIMESTAMP | Timestamp ultimo attacco |
| **last_update** | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | Timestamp ultimo aggiornamento |
| **is_blocked** | BOOLEAN DEFAULT FALSE | Flag blocco IP |
| **notes** | TEXT | Note aggiuntive |

### TRUST_REDUCTION_LOG (Policy 1)
Mantiene lo storico di tutte le riduzioni del trust score per audit e analisi.

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| **id** | SERIAL PRIMARY KEY | Identificatore univoco |
| **ip_address** | INET NOT NULL | Indirizzo IP interessato |
| **reduction_amount** | INTEGER NOT NULL | Quantità di riduzione |
| **reason** | TEXT NOT NULL | Motivo della riduzione |
| **attack_count** | INTEGER | Numero attacchi al momento della riduzione |
| **timestamp** | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | Timestamp della riduzione |
| **applied_by** | TEXT DEFAULT 'system' | Chi ha applicato la riduzione |

## Vincoli e Funzioni

### Trigger per Trust Score Default
Assegna automaticamente il trust score base in base al ruolo dell'utente se non specificato.

```sql
CREATE OR REPLACE FUNCTION set_trust_score_default()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.trust_score IS NULL THEN
        CASE NEW.ruolo
            WHEN 'direttore' THEN NEW.trust_score := 85;
            WHEN 'cassiere' THEN NEW.trust_score := 70;
            WHEN 'consulente' THEN NEW.trust_score := 75;
            WHEN 'cliente' THEN NEW.trust_score := 60;
            ELSE NEW.trust_score := 50;
        END CASE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Funzione per Aggiornamento Network Trust
Gestisce la riduzione progressiva del trust score garantendo che rimanga sempre nel range 0-100.

```sql
CREATE OR REPLACE FUNCTION update_network_trust(
    p_ip_address INET,
    p_reduction INTEGER,
    p_reason TEXT,
    p_attack_count INTEGER
)
RETURNS VOID AS $$
BEGIN
    -- Gestisce la riduzione progressiva del trust score
    -- Garantisce che il valore rimanga tra 0 e 100
    INSERT INTO network_trust (ip_address, current_trust_score, attack_count, last_attack_time, last_update)
    VALUES (p_ip_address, 100 - p_reduction, p_attack_count, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    ON CONFLICT (ip_address) 
    DO UPDATE SET 
        current_trust_score = GREATEST(network_trust.current_trust_score - p_reduction, 0),
        attack_count = p_attack_count,
        last_attack_time = CURRENT_TIMESTAMP,
        last_update = CURRENT_TIMESTAMP,
        is_blocked = CASE WHEN (network_trust.current_trust_score - p_reduction) <= 20 THEN TRUE ELSE network_trust.is_blocked END;
    
    -- Log della riduzione
    INSERT INTO trust_reduction_log (ip_address, reduction_amount, reason, attack_count)
    VALUES (p_ip_address, p_reduction, p_reason, p_attack_count);
END;
$$ LANGUAGE plpgsql;
```

## Relazioni

1. **UTENTI** ↔ **UTENTI_IP**: Un utente può avere più IP (1:N)
2. **UTENTI** ↔ **FILE_DOCUMENTI**: Un utente può possedere più file (1:N)
3. **UTENTI** ↔ **ACCESS_LOG**: Un utente può avere più log di accesso (1:N)
4. **FILE_DOCUMENTI** ↔ **ACCESS_LOG**: Un file può avere più log di accesso (1:N)
5. **NETWORK_TRUST** ↔ **TRUST_REDUCTION_LOG**: Un IP può avere più riduzioni di fiducia (1:N)

## Soglie Zero Trust

### Trust Score Utenti (Base)
- **Direttore**: 85/100
- **Cassiere**: 70/100  
- **Consulente**: 75/100
- **Cliente**: 60/100

### Soglie Operazioni
- **Dati Personali Clienti**: Lettura 60+, Scrittura 80+
- **Dati Transazionali**: Lettura 65+, Scrittura 75+
- **Documenti Operativi**: Lettura 60+, Scrittura 70+

### Network Trust Actions
- **Trust ≤ 20**: IP bloccato completamente
- **Trust ≤ 40**: Banda limitata a 50 kbps
- **Trust ≤ 60**: Banda limitata a 200 kbps
- **Trust > 60**: Nessuna restrizione

## Policy Implementate

### Policy 1: Riduzione Automatica Fiducia Reti
**Descrizione**: Le reti con più di 10 tentativi di attacco negli ultimi 30 giorni ricevono una riduzione automatica della fiducia di 25-30 punti.

**Implementazione**:
- Monitoraggio automatico tramite Splunk
- Riduzione progressiva del trust score
- Applicazione automatica di regole IPTables
- Logging completo delle azioni intraprese

## Indici per Performance

Il database include indici ottimizzati per le query più frequenti:

```sql
-- Indici principali
CREATE INDEX idx_network_trust_ip ON network_trust(ip_address);
CREATE INDEX idx_network_trust_score ON network_trust(current_trust_score);
CREATE INDEX idx_network_trust_blocked ON network_trust(is_blocked);
CREATE INDEX idx_trust_reduction_log_ip ON trust_reduction_log(ip_address);
CREATE INDEX idx_trust_reduction_log_timestamp ON trust_reduction_log(timestamp);
CREATE INDEX idx_utenti_username ON utenti(username);
CREATE INDEX idx_utenti_ip_address ON utenti_ip(ip_address);
CREATE INDEX idx_access_log_utente ON access_log(utente_id);
CREATE INDEX idx_access_log_file ON access_log(file_id);
CREATE INDEX idx_access_log_timestamp ON access_log(timestamp);
```

## File di Setup

### schema.sql
Contiene la definizione completa dello schema database:
- Tipi ENUM
- Tabelle con vincoli
- Funzioni e trigger
- Indici per performance

### data.sql
Contiene dati di esempio per testing:
- Utenti con diversi ruoli
- Associazioni IP-utente
- File con diversi livelli di sensibilità
- Log di accesso di esempio
- Esempi di network trust e riduzioni

## Query Utili

### Monitoraggio Trust Score
```sql
-- IP con trust score basso
SELECT ip_address, current_trust_score, attack_count, is_blocked
FROM network_trust 
WHERE current_trust_score <= 40
ORDER BY current_trust_score ASC;

-- Storico riduzioni recenti
SELECT ip_address, reduction_amount, reason, timestamp
FROM trust_reduction_log 
ORDER BY timestamp DESC 
LIMIT 10;
```

### Analisi Accessi
```sql
-- Accessi negati per trust insufficiente
SELECT u.username, u.ruolo, u.trust_score, al.azione, al.motivazione
FROM access_log al
JOIN utenti u ON al.utente_id = u.id
WHERE al.esito = FALSE
AND al.motivazione LIKE '%Trust%'
ORDER BY al.timestamp DESC;
```

### Report Sicurezza
```sql
-- Distribuzione trust score di rete
SELECT 
    CASE 
        WHEN current_trust_score > 80 THEN 'Alto'
        WHEN current_trust_score > 60 THEN 'Medio'
        WHEN current_trust_score > 20 THEN 'Basso'
        ELSE 'Bloccato'
    END as trust_level,
    COUNT(*) as count
FROM network_trust
GROUP BY trust_level
ORDER BY MIN(current_trust_score) DESC;
```

## Sicurezza

### Controlli Implementati
- **Validazione dati**: Vincoli su tutti i campi critici
- **Audit trail**: Log completo di tutti gli accessi
- **Integrità referenziale**: Foreign key con CASCADE appropriati
- **Range validation**: Trust score sempre tra 0-100

### Best Practices
- Backup regolari del database
- Monitoraggio delle query lente
- Pulizia periodica dei log vecchi
- Analisi regolare dei pattern di accesso

---

**Versione**: 1.0  
**Ultima modifica**: 2025-01-XX  
**Compatibilità**: PostgreSQL 14+
    
