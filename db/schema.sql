-- Tipi ENUM
CREATE TYPE ruolo_enum AS ENUM ('cassiere', 'manager', 'auditor');
CREATE TYPE sensibilita_enum AS ENUM ('sensibile', 'non_sensibile');
CREATE TYPE azione_enum AS ENUM ('lettura', 'scrittura');

-- Tabella utenti
CREATE TABLE utenti (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    ruolo ruolo_enum NOT NULL
);

-- Tabella file
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
