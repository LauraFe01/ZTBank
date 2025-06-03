import requests
import time
import logging

logging.basicConfig(level=logging.INFO)

SPLUNK_API_BASE = "https://splunk:8089"
SPLUNK_AUTH = ("admin", "Micol0301!")

def splunk_search(query):
    r = requests.post(
        f"{SPLUNK_API_BASE}/services/search/jobs",
        auth=SPLUNK_AUTH,
        verify=False,
        data={
            "search": f"search {query}",
            "output_mode": "json",
        },
    )
    
    sid = r.json().get("sid")
    if not sid:
        return []

    # Aspetta che il job sia completato
    if not wait_for_job(sid):
        return []

    # Ottieni i risultati
    r2 = requests.get(
        f"{SPLUNK_API_BASE}/services/search/jobs/{sid}/results",
        auth=SPLUNK_AUTH,
        verify=False,
        params={"output_mode": "json"},
    )
    logging.info(f"Splunk search response: {r2.json()}")

    return r2.json().get("results", [])


def wait_for_job(sid, timeout=10):
    """Attende che il job Splunk sia completato."""
    for _ in range(timeout):
        status = requests.get(
            f"{SPLUNK_API_BASE}/services/search/jobs/{sid}",
            auth=SPLUNK_AUTH,
            verify=False,
            params={"output_mode": "json"},
        ).json()

        is_done = status["entry"][0]["content"].get("isDone", False)
        if is_done:
            return True
        time.sleep(1)
    return False