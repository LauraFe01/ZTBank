-- Utenti di esempio
INSERT INTO utenti (username, ruolo, codice_fiscale, indirizzo, email, telefono, trust_score) VALUES
('direttore1', 'direttore', 'DRTRCF01A01H501Z', 'Via Direzione 1', 'direttore1@banca.it', '0123456789', 85),
('cassiere1', 'cassiere', 'CSSRCF01A01H501Z', 'Via Cassa 1', 'cassiere1@banca.it', '0123456790', 70),
('consulente1', 'consulente', 'CNSLCF01A01H501Z', 'Via Consulenza 1', 'consulente1@banca.it', '0123456791', 75),
('cliente1', 'cliente', 'CLNTCF01A01H501Z', 'Via Cliente 1', 'cliente1@banca.it', '0123456792', 60);

-- Associazione utenti-IP
INSERT INTO utenti_ip (utente_id, ip_address, ip_ruolo) VALUES
(1, '192.168.1.10', 'internal'),
(2, '10.0.0.5', 'wifi'),
(3, '203.0.113.42', 'external'),
(4, '192.168.1.20', 'internal');

-- File/documenti di esempio
INSERT INTO file_documenti (nome_file, contenuto, sensibilita, proprietario_id) VALUES
('Dati Personali Cliente1', 'Nome: Mario Rossi\nCF: CLNTCF01A01H501Z\n...', 'sensibile', 4),
('Saldo Cliente1', 'Saldo: 10000 EUR', 'sensibile', 4),
('Ricevuta Bonifico Cliente1', 'Bonifico in entrata: 500 EUR', 'sensibile', 4),
('Elenco Clienti', 'Cliente1, Cliente2, ...', 'non_sensibile', 1),
('Piano Investimento', 'Piano: Azionario', 'non_sensibile', 3);

-- Access log di esempio
INSERT INTO access_log (utente_id, file_id, azione, esito, motivazione) VALUES
(1, 1, 'lettura', TRUE, 'Supervisione'),
(2, 2, 'scrittura', TRUE, 'Aggiornamento saldo'),
(3, 5, 'lettura', TRUE, 'Analisi investimento'),
(4, 1, 'lettura', TRUE, 'Accesso ai propri dati');