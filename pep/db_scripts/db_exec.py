from db_scripts.db_DAO import FileDocumentoDAO
import logging


logging.basicConfig(level=logging.INFO)


def execute_single_operation(operation, doc_id, role):
    """
    Esegue un'operazione di lettura o cancellazione su un documento nel database.

    Args:
        operation (str): Tipo di operazione ('read' o 'delete').
        doc_id (int): ID del documento su cui eseguire l'operazione.
        role (str): Ruolo dell'utente che richiede l'operazione.

    Returns:
        dict o bool: Documento trovato (per 'read'), True/False (per 'delete'), None in caso di errore.
    """
    db_dao = FileDocumentoDAO()

    try:
        logging.info(f"[DB_EXEC] Operazione: {operation}, DocID: {doc_id}, Ruolo: {role}")
        if operation == "read":
            result = db_dao.get_file_documento_by_id(doc_id)
            if not result:
                logging.warning("[DB_EXEC] Documento non trovato")
                return None
            sensibilita = result[3]  # Assumendo che 'sensibilita' sia il 4° campo
            if sensibilita == 'sensibile' and role != "Direttore":
                logging.warning("[DB_EXEC] Accesso negato a documento sensibile per ruolo: %s", role)
                return None
            return result

        elif operation == "delete":
            deleted = db_dao.delete_file_documento(doc_id)
            logging.info(f"[DB_EXEC] Documento eliminato: {deleted}")
            return deleted

        else:
            logging.warning(f"[DB_EXEC] Operazione non valida: {operation}")
            return None

    except Exception as e:
        logging.error(f"[DB_EXEC] Errore: {e}")
        return None


def execute_write_operation(nome_file, contenuto, sensibilita):
    """
    Inserisce un nuovo documento nel database.

    Args:
        nome_file (str): Nome del file da inserire.
        contenuto (str): Contenuto del file.
        sensibilita (str): Livello di sensibilità del documento.

    Returns:
        int o bool: ID del documento inserito, False in caso di errore.
    """
    db_dao = FileDocumentoDAO()
    try:
        logging.info(f"[DB_EXEC] Inserimento file: {nome_file}")
        inserted_id = db_dao.insert_file_documento(nome_file, contenuto, sensibilita)
        logging.info(f"[DB_EXEC] Inserito con ID: {inserted_id}")
        return inserted_id
    except Exception as e:
        logging.error(f"[DB_EXEC] Errore: {e}")
        return False