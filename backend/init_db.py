import requests
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongo:27017/formula1")
client = MongoClient(MONGODB_URI)
db = client.formula1

BASE_URL = "https://api.openf1.org/v1"


def fetch_and_store(endpoint: str, collection_name: str):
    url = f"{BASE_URL}/{endpoint}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if not data:
            logger.warning(f"Brak danych z endpointu {url}")
            return

        # Filtrowanie unikalnych kierowców
        if collection_name == "drivers":
            seen = set()
            unique_drivers = []
            for driver in data:
                identifier = driver.get("driver_number") or driver.get("full_name")
                if identifier and identifier not in seen:
                    seen.add(identifier)
                    unique_drivers.append(driver)
            data = unique_drivers
            logger.info(f"Przefiltrowano do {len(data)} unikalnych kierowców")

        db[collection_name].delete_many({})
        db[collection_name].insert_many(data)
        logger.info(f"Zapisano {len(data)} rekordów do kolekcji '{collection_name}'")

    except Exception as e:
        logger.error(f"Błąd przy pobieraniu danych z {url}: {e}")


def fetch_results_for_recent_sessions():
    try:
        sessions = list(db.sessions.find({}, {"session_key": 1}).sort("session_key", -1))
        for session in sessions:
            session_key = session["session_key"]
            url = f"{BASE_URL}/results?session_key={session_key}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data:
                db.results.delete_many({"session_key": session_key})
                db.results.insert_many(data)
                logger.info(f"Zapisano wyniki dla sesji {session_key}")
    except Exception as e:
        logger.error(f"Błąd przy pobieraniu wyników sesji: {e}")

def init_database():
    logger.info("Rozpoczynam inicjalizację bazy danych...")
    fetch_and_store("drivers", "drivers")
    # fetch_and_store("teams", "teams")
    fetch_and_store("sessions", "sessions")
    fetch_results_for_recent_sessions()
    logger.info("Zakończono inicjalizację bazy danych.")

init_database()
