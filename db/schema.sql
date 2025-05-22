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