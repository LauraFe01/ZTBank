# Logica del DB

## Entità principali

| Tabella         | Descrizione                                           |
|-----------------|--------------------------------------------------------|
| `utenti`        | Anagrafica utenti con ruolo (es. cassiere, manager)   |
| `file_documenti`| File presenti nel sistema con livello di sensibilità |
| `access_log`    | Tracciamento di ogni accesso (concesso o negato)     |

## Tipi definiti

- `ruolo_enum`: `cassiere`, `manager`, `auditor`
- `sensibilita_enum`: `sensibile`, `non_sensibile`

---

## 🔗 Integrazione con l'API Flask

La logica di controllo accessi è integrata nel file `router/api/app.py`:

1. Flask riceve i webhook da Splunk (via `/splunk-webhook-db`)
2. Viene estratto il payload (`username`, `file_name`, `azione`)
3. Il server recupera dal DB le info su utente e file
4. La funzione `verifica_accesso()` decide se consentire o negare
5. L’azione viene loggata nella tabella `access_log` con esito e motivazione