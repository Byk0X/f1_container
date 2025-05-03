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
    # Specjalne traktowanie endpointu 'drivers'
    if endpoint == "drivers":
        url = f"{BASE_URL}/{endpoint}?meeting_key=latest"
    else:
        url = f"{BASE_URL}/{endpoint}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if not data:
            logger.warning(f"Brak danych z endpointu {url}")
            return

        # Filtrowanie unikalnych kierowców z ostatniego wyścigu
        if collection_name == "drivers":
            seen = set()
            unique_drivers = []
            for driver in data:
                identifier = driver.get("driver_number") or driver.get("full_name")
                if identifier and identifier not in seen:
                    seen.add(identifier)
                    unique_drivers.append(driver)
            data = unique_drivers
            logger.info(f"Przefiltrowano do {len(data)} unikalnych kierowców z ostatniego wyścigu")

        db[collection_name].delete_many({})
        db[collection_name].insert_many(data)
        logger.info(f"Zapisano {len(data)} rekordów do kolekcji '{collection_name}'")

    except Exception as e:
        logger.error(f"Błąd przy pobieraniu danych z {url}: {e}")



def fetch_f1_teams():
    try:
        drivers = list(db["drivers"].find({}, {"team_name": 1}))
        unique_teams = {}
        for driver in drivers:
            team_name = driver.get("team_name")
            if team_name and team_name not in unique_teams:
                unique_teams[team_name] = {"team_name": team_name}

        if unique_teams:
            db["teams"].delete_many({})
            db["teams"].insert_many(list(unique_teams.values()))
            logger.info(f"Zapisano {len(unique_teams)} unikalnych zespołów F1 na podstawie kierowców.")
        else:
            logger.warning("Nie znaleziono żadnych zespołów F1 do zapisania na podstawie kierowców.")

    except Exception as e:
        logger.error(f"Błąd przy pobieraniu zespołów F1 z kolekcji 'drivers': {e}")

def fetch_and_store_2025_results():
    url = "https://api.jolpi.ca/ergast/f1/2025/results.json?limit=1000000"
    print("Pobieranie wszystkich danych z sezonu 2025...")
    response = requests.get(url)
    if response.status_code != 200:
        print("Błąd pobierania danych.")
        return

    data = response.json()
    races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    if not races:
        print("Brak danych wyścigów.")
        return

    all_results = []

    for race in races:
        race_results = race.get("Results", [])
        for result in race_results:
            result["raceName"] = race["raceName"]
            result["round"] = int(race["round"])
            result["date"] = race["date"]
            result["circuit"] = race["Circuit"]["circuitName"]
            all_results.append(result)

    db.results_2025.delete_many({})
    db.results_2025.insert_many(all_results)
    print(f"Zapisano {len(all_results)} wyników do kolekcji 'results_2025'.")

def fetch_and_store_qualifying_results():
    url = "https://api.jolpi.ca/ergast/f1/2025/qualifying.json?limit=1000000"
    print("Pobieranie wszystkich danych z sezonu 2025...")
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Błąd pobierania danych.")
        return
    
    data = response.json()
    qualifications = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    
    if not qualifications:
        print("Brak danych wyścigów.")
        return
    
    all_results = []

    for qualification in qualifications:
        qualification_results = qualification.get("Results", [])
        for result in qualification_results:
            result["raceName"] = qualification["raceName"]
            result["round"] = int(qualification["round"])
            result["date"] = qualification["date"]
            result["circuit"] = qualification["Circuit"]["circuitName"]
            all_results.append(result)

    db.qualifying_results.delete_many({})
    db.qualifying_results.insert_many(all_results)
    print(f"Zapisano {len(all_results)} wyników do kolekcji 'qualifying_results'.")
    
def fetch_and_store_sprint_results():
    url = "https://api.jolpi.ca/ergast/f1/2025/sprint.json?limit=1000000"
    print("Pobieranie wszystkich danych zjiraza 2025...")
    response = requests.get(url)

    if response.status_code != 200:
        print("Błąd pobierania danych.")
        return

    data = response.json()
    sprints = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])

    if not sprints:
        print("Brak danych wyścigów.")
        return
    
    all_results = []

    for sprint in sprints:
        sprint_results = sprint.get("Results", [])
        for result in sprint_results:
            result["raceName"] = sprint["raceName"]
            result["round"] = int(sprint["round"])
            result["date"] = sprint["date"]
            result["circuit"] = sprint["Circuit"]["circuitName"]
            all_results.append(result)

    db.sprint_results.delete_many({})
    db.sprint_results.insert_many(all_results)
    print(f"Zapisano {len(all_results)} wyników do kolekcji 'sprint_results'.")
    

def init_database():
    logger.info("Rozpoczynam inicjalizację bazy danych...")
    fetch_and_store("drivers", "drivers")
    fetch_f1_teams()
    fetch_and_store_2025_results()
    logger.info("Zakończono inicjalizację bazy danych.")

init_database()
