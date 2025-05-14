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

        if collection_name == "drivers":
            seen = set()
            unique_drivers = []
            for driver in data:
                identifier = driver.get("driver_number") or driver.get("full_name")
                if identifier and identifier not in seen:
                    seen.add(identifier)
                    unique_drivers.append(driver)
            data = unique_drivers
            logger.info(
                f"Przefiltrowano do {len(data)} unikalnych kierowców z ostatniego wyścigu"
            )

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
            logger.info(
                f"Zapisano {len(unique_teams)} unikalnych zespołów F1 na podstawie kierowców."
            )
        else:
            logger.warning(
                "Nie znaleziono żadnych zespołów F1 do zapisania na podstawie kierowców."
            )

    except Exception as e:
        logger.error(f"Błąd przy pobieraniu zespołów F1 z kolekcji 'drivers': {e}")


def fetch_and_store_2025_results():
    base_url = "https://api.jolpi.ca/ergast/f1/2025/results.json"
    limit = 100
    offset = 0
    total = None
    all_results = []

    print("Pobieranie wszystkich danych wyścigów 2025...")

    while True:
        url = f"{base_url}?limit={limit}&offset={offset}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Błąd pobierania danych przy offset={offset}.")
            break

        data = response.json()
        mrdata = data.get("MRData", {})
        total = int(mrdata.get("total", 0))
        races = mrdata.get("RaceTable", {}).get("Races", [])

        if not races:
            break

        for race in races:
            race_results = race.get("Results", [])
            for result in race_results:
                result["raceName"] = race["raceName"]
                result["round"] = int(race["round"])
                result["date"] = race["date"]
                result["circuit"] = race["Circuit"]["circuitName"]
                all_results.append(result)

        offset += limit
        if offset >= total:
            break

    if all_results:
        db.results_2025.delete_many({})
        db.results_2025.insert_many(all_results)
        print(f"Zapisano {len(all_results)} wyników do kolekcji 'results_2025'.")
    else:
        print("Brak danych do zapisania.")


def fetch_and_store_qualifying_results():
    base_url = "https://api.jolpi.ca/ergast/f1/2025/qualifying.json"
    limit = 100
    offset = 0
    total = None
    all_results = []

    print("Pobieranie wszystkich danych z kwalifikacji 2025...")

    while True:
        url = f"{base_url}?limit={limit}&offset={offset}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Błąd pobierania danych przy offset={offset}.")
            break

        data = response.json()
        mrdata = data.get("MRData", {})
        total = int(mrdata.get("total", 0))
        races = mrdata.get("RaceTable", {}).get("Races", [])

        if not races:
            break

        for qualification in races:
            qualification_results = qualification.get("QualifyingResults", [])
            for result in qualification_results:
                result["raceName"] = qualification["raceName"]
                result["round"] = int(qualification["round"])
                result["date"] = qualification["date"]
                result["circuit"] = qualification["Circuit"]["circuitName"]
                all_results.append(result)

        offset += limit
        if offset >= total:
            break

    if all_results:
        db.qualifying_results.delete_many({})
        db.qualifying_results.insert_many(all_results)
        print(f"Zapisano {len(all_results)} wyników do kolekcji 'qualifying_results'.")
    else:
        print("Brak danych do zapisania.")


def fetch_and_store_sprint_results():
    base_url = "https://api.jolpi.ca/ergast/f1/2025/sprint.json"
    limit = 100
    offset = 0
    total = None
    all_results = []

    print("Pobieranie wszystkich danych ze sprintów 2025...")

    while True:
        url = f"{base_url}?limit={limit}&offset={offset}"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Błąd pobierania danych przy offset={offset}.")
            break

        data = response.json()
        mrdata = data.get("MRData", {})
        total = int(mrdata.get("total", 0))
        races = mrdata.get("RaceTable", {}).get("Races", [])

        if not races:
            break

        for sprint in races:
            sprint_results = sprint.get("SprintResults", [])
            for result in sprint_results:
                result["raceName"] = sprint["raceName"]
                result["round"] = int(sprint["round"])
                result["date"] = sprint["date"]
                result["circuit"] = sprint["Circuit"]["circuitName"]
                all_results.append(result)

        offset += limit
        if offset >= total:
            break

    if all_results:
        db.sprint_results.delete_many({})
        db.sprint_results.insert_many(all_results)
        print(f"Zapisano {len(all_results)} wyników do kolekcji 'sprint_results'.")
    else:
        print("Brak danych do zapisania.")


def fetch_and_store_constructors_standings():
    base_url = "https://api.jolpi.ca/ergast/f1/2025/constructorstandings.json"
    limit = 100
    offset = 0
    total = None
    all_standings = []

    print("Pobieranie danych klasyfikacji konstruktorów 2025...")

    while True:
        url = f"{base_url}?limit={limit}&offset={offset}"
        response = requests.get(url)

        if response.status_code != 200:
            print(
                f"Błąd pobierania danych przy offset={offset}: {response.status_code}"
            )
            break

        data = response.json()
        mrdata = data.get("MRData", {})
        total = int(mrdata.get("total", 0))
        standings_lists = mrdata.get("StandingsTable", {}).get("StandingsLists", [])

        if not standings_lists:
            break

        for standings in standings_lists:
            season = standings.get("season")
            round_number = standings.get("round")
            for standing in standings.get("ConstructorStandings", []):
                standing["season"] = season
                standing["round"] = round_number
                all_standings.append(standing)

        offset += limit
        if offset >= total:
            break

    if all_standings:
        db.constructor_standings.delete_many({})
        db.constructor_standings.insert_many(all_standings)
        print(
            f"Zapisano {len(all_standings)} wyników do kolekcji 'constructor_standings'."
        )
    else:
        print("Brak danych do zapisania.")


def fetch_and_store_driver_standings():
    base_url = "https://api.jolpi.ca/ergast/f1/2025/driverstandings.json"
    limit = 100
    offset = 0
    total = None
    all_standings = []

    print("Pobieranie danych klasyfikacji kierowców 2025...")

    while True:
        url = f"{base_url}?limit={limit}&offset={offset}"
        response = requests.get(url)

        if response.status_code != 200:
            print(
                f"Błąd pobierania danych przy offset={offset}: {response.status_code}"
            )
            break

        data = response.json()
        mrdata = data.get("MRData", {})
        total = int(mrdata.get("total", 0))
        standings_lists = mrdata.get("StandingsTable", {}).get("StandingsLists", [])

        if not standings_lists:
            break

        for standings in standings_lists:
            season = standings.get("season")
            round_number = standings.get("round")
            for standing in standings.get("DriverStandings", []):
                standing["season"] = season
                standing["round"] = round_number
                all_standings.append(standing)

        offset += limit
        if offset >= total:
            break

    if all_standings:
        db.driver_standings.delete_many({})
        db.driver_standings.insert_many(all_standings)
        print(f"Zapisano {len(all_standings)} wyników do kolekcji 'driver_standings'.")
    else:
        print("Brak danych do zapisania.")


def init_database():
    logger.info("Rozpoczynam inicjalizację bazy danych...")
    fetch_and_store("drivers", "drivers")
    fetch_f1_teams()
    fetch_and_store_2025_results()
    logger.info("Pobieram dane o kwalifikacjach...")
    fetch_and_store_qualifying_results()
    logger.info("Pobieram dane o sprintach...")
    fetch_and_store_sprint_results()
    logger.info("Pobieram dane o punktach konstruktorów...")
    fetch_and_store_constructors_standings()
    logger.info("Pobieram dane o punktach kierowców...")
    fetch_and_store_driver_standings()
    logger.info("Zakończono inicjalizację bazy danych.")


init_database()
