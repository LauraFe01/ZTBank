-- Tipi ENUM
CREATE TYPE sensibilita_enum AS ENUM ('sensibile', 'non_sensibile');

-- Tabella file_documenti (risorse)
CREATE TABLE file_documenti (
    id SERIAL PRIMARY KEY,
    nome_file TEXT NOT NULL,
    contenuto TEXT,
    sensibilita sensibilita_enum NOT NULL
);