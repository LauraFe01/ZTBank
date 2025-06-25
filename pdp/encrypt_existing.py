import json
import os
from cryptography.fernet import Fernet

def encrypt_trust_file(file_path="trust_db.json", key_env_var="TRUST_KEY"):
    """
    Cifra il contenuto di un file JSON utilizzando una chiave simmetrica.

    Il file viene letto, verificato come JSON valido e poi cifrato con una chiave
    ottenuta da una variabile d'ambiente. Il contenuto cifrato sovrascrive il file originale.

    Args:
        file_path (str): Percorso al file JSON da cifrare. Default: 'trust_db.json'.
        key_env_var (str): Nome della variabile d'ambiente contenente la chiave. Default: 'TRUST_KEY'.

    Returns:
        bool: True se la cifratura è andata a buon fine, False altrimenti.
    """

    if key_env_var not in os.environ:
        print(f"❌ Variabile d'ambiente {key_env_var} non trovata.")
        return False

    key = os.environ[key_env_var].encode()
    fernet = Fernet(key)

    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Verifica che il contenuto sia JSON valido
        json_data = json.loads(content)

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
