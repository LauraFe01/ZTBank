-- Tipi ENUM
CREATE TYPE ruolo_enum AS ENUM ('direttore', 'cassiere', 'consulente', 'cliente');
CREATE TYPE sensibilita_enum AS ENUM ('sensibile', 'non_sensibile');
CREATE TYPE azione_enum AS ENUM ('lettura', 'scrittura', 'cancellazione');
CREATE TYPE ip_ruolo_enum AS ENUM ('internal', 'external', 'wifi');

-- Funzione per assegnare trust_score base in base al ruolo SOLO se non specificato
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

-- Tabella utenti 
-- (trust_score è opzionale, se non specificato si assegna di default)
CREATE TABLE utenti (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    ruolo ruolo_enum NOT NULL,
    codice_fiscale TEXT UNIQUE NOT NULL,
    indirizzo TEXT,
    email TEXT,
    telefono TEXT,
    trust_score INTEGER
);

-- Trigger per la tabella utenti
CREATE TRIGGER utenti_trust_score_default
BEFORE INSERT ON utenti
FOR EACH ROW
EXECUTE FUNCTION set_trust_score_default();

-- Tabella associazione utenti <-> indirizzi IP
CREATE TABLE utenti_ip (
    id SERIAL PRIMARY KEY,
    utente_id INTEGER REFERENCES utenti(id) ON DELETE CASCADE,
    ip_address INET NOT NULL,
    ip_ruolo ip_ruolo_enum NOT NULL,
    UNIQUE(utente_id, ip_address)
);

-- Tabella file_documenti (risorse)
CREATE TABLE file_documenti (
    id SERIAL PRIMARY KEY,
    nome_file TEXT NOT NULL,
    contenuto TEXT,
    sensibilita sensibilita_enum NOT NULL,
    proprietario_id INTEGER REFERENCES utenti(id)
);

-- Tabella accessi richiesti o effettuati
CREATE TABLE access_log (
    id SERIAL PRIMARY KEY,
    utente_id INTEGER REFERENCES utenti(id),
    file_id INTEGER REFERENCES file_documenti(id),
    azione azione_enum NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    esito BOOLEAN NOT NULL,
    motivazione TEXT
);


-- AGGIUNTA LA PARTE SEGUENTE PER POLICY 1

-- Tabella per tracciare la fiducia delle reti/IP
CREATE TABLE network_trust (
    id SERIAL PRIMARY KEY,
    ip_address INET NOT NULL UNIQUE,
    initial_trust_score INTEGER DEFAULT 100,
    current_trust_score INTEGER DEFAULT 100,
    attack_count INTEGER DEFAULT 0,
    last_attack_time TIMESTAMP,
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_blocked BOOLEAN DEFAULT FALSE,
    notes TEXT
);

-- Tabella per log delle riduzioni di fiducia
CREATE TABLE trust_reduction_log (
    id SERIAL PRIMARY KEY,
    ip_address INET NOT NULL,
    reduction_amount INTEGER NOT NULL,
    reason TEXT NOT NULL,
    attack_count INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    applied_by TEXT DEFAULT 'system'
);

-- Funzione per aggiornare il trust score
CREATE OR REPLACE FUNCTION update_network_trust(
    p_ip_address INET,
    p_reduction INTEGER,
    p_reason TEXT,
    p_attack_count INTEGER
)
RETURNS VOID AS $$
BEGIN
    -- Inserisci o aggiorna il record nella tabella network_trust
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