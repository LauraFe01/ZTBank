import json, os
from cryptography.fernet import Fernet

def encrypt_trust_file(file_path="trust_db.json", key_env_var="TRUST_KEY"):
    """Cifra il file trust_db.json con la chiave in TRUST_KEY."""
    if key_env_var not in os.environ:
        print(f"❌ Variabile d'ambiente {key_env_var} non trovata.")
        return False

    key = os.environ[key_env_var].encode()
    fernet = Fernet(key)

    try:
        with open(file_path, "r") as f:
            content = f.read()
        json_data = json.loads(content)  # Verifica validità
    except Exception as e:
        print(f"❌ Errore nella lettura/parsing del file: {e}")
        return False

    encrypted = fernet.encrypt(content.encode())

    try:
        with open(file_path, "wb") as f:
            f.write(encrypted)
        print("✅ File cifrato con successo.")
        return True
    except Exception as e:
        print(f"❌ Errore durante la scrittura del file cifrato: {e}")
        return False

