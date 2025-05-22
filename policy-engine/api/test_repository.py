from utils.db import DBConnection
from utils.repository.repository import Repository

def main():
    conn = DBConnection().get_conn()
    repo = Repository(conn)

    print("CREA UTENTE:")
    user = repo.create_user(
        username="testuser",
        ruolo="cliente",
        codice_fiscale="TSTUSR01A01H501Z",
        indirizzo="Via Test 1",
        email="testuser@banca.it",
        telefono="0123456799",
        trust_score=None
    )
    print(user)

    print("LEGGI UTENTE PER USERNAME:")
    user = repo.get_user_by_username("testuser")
    print(user)

    print("AGGIORNA UTENTE:")
    updated = repo.update_user(user[0], telefono="0999999999")
    print(updated)

    print("CANCELLA UTENTE:")
    repo.delete_user(user[0])
    print("Utente cancellato.")

if __name__ == "__main__":
    main()