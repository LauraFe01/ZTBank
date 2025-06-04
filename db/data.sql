-- File/documenti di esempio
INSERT INTO file_documenti (nome_file, contenuto, sensibilita) VALUES
('Dati Personali Cliente1', 'Nome: Mario Rossi\nCF: CLNTCF01A01H501Z\n...', 'sensibile'),
('Saldo Cliente1', 'Saldo: 10000 EUR', 'sensibile'),
('Ricevuta Bonifico Cliente1', 'Bonifico in entrata: 500 EUR', 'sensibile'),
('Elenco Clienti', 'Cliente1, Cliente2, ...', 'non_sensibile'),
('Piano Investimento', 'Piano: Azionario', 'non_sensibile'),
('Documento Identità Cliente4', 'Tipo: Carta Identità\nNumero: X1234567', 'sensibile'),
('Comunicazione Interna', 'Meeting lunedì ore 10:00', 'non_sensibile'),
('Fattura Cliente5', 'Importo: 1.250 EUR\nData: 2025-05-20', 'sensibile'),
('Registro Accessi', 'Accessi registrati dal 01/05 al 31/05', 'non_sensibile'),
('Questionario MIFID', 'Esito: Cliente con conoscenze elevate', 'sensibile');