-- Inserisci utenti
INSERT INTO utenti (username, ruolo) VALUES
('alice', 'cassiere'),
('bob', 'manager'),
('carol', 'auditor');

-- Inserisci file
INSERT INTO file_documenti (nome_file, contenuto, sensibilita, proprietario_id) VALUES
('conto_corrente_2024.txt', 'Saldo: 4500€', 'sensibile', 2),
('offerte_promozionali.txt', 'Promozione mutui 2024', 'non_sensibile', 2),
('log_sicurezza.txt', 'Accessi sospetti rilevati', 'sensibile', 3);
