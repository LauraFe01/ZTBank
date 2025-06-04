from user_auth import load_user_db, create_user
import logging

logging.basicConfig(level=logging.INFO)

# Mappa ruoli → utenti da creare
utenti = {
    "1": ("giovanni.rossi", "pass_direttore", "Direttore"),
    "2": ("marco.bianchi", "pass_cassiere", "Cassiere"),
    "3": ("luca.verdi", "pass_consulente", "Consulente"),
    "4": ("maria.neri", "pass_cliente", "Cliente")
}

db = load_user_db()

for key, (username, password, role) in utenti.items():
    ok, msg = create_user(username, password, role, db)
    logging.info(f"[{role}] {'✅' if ok else '❌'} {msg}")

db = load_user_db()
logging.info(f"DB utenti: {db}")