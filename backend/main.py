from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import logging
import threading
import time
import json
from datetime import datetime
from init_db import init_database
import requests
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


load_dotenv()


app = FastAPI(title="F1 Data API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongo:27017/formula1")

try:
    client = MongoClient(MONGODB_URI)
    db = client.formula1
    logger.info("Połączono z bazą danych MongoDB")
except Exception as e:
    logger.error(f"Błąd połączenia z MongoDB: {e}")
    raise

# Zdefiniuj funkcję do regularnego odświeżania danych
def refresh_data():
    logger.info("Rozpoczęto odświeżanie danych...")
    try:
        init_database()
    except Exception as e:
        logger.error(f"Błąd podczas odświeżania danych: {e}")
    logger.info("Zakończono odświeżanie danych")

#Background refresh
def background_refresh():
    while True:
        time.sleep(6 * 60 * 60)  #Each 6 hours
        refresh_data()

#Thread to run background_refresh
@app.on_event("startup")
def on_startup():
    threading.Thread(target=background_refresh, daemon=True).start()
    logger.info("Harmonogram odświeżania danych uruchomiony")

@app.get("/")
def read_root():
    return {"message": "F1 Data API działa!"}

@app.get("/sessions", response_model=List[Dict[str, Any]])
async def get_sessions():
    try:
        sessions = list(db.sessions.find({}, {'_id': 0}))
        return sessions
    except Exception as e:
        logger.error(f"Błąd podczas pobierania danych o sesjach: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/results_2025", response_class=JSONResponse)
async def get_results_2025(round: Optional[int] = Query(None, description="Numer rundy")):
    try:
        query = {}
        if round is not None:
            query["round"] = round

        results = list(db.results_2025.find(query, {"_id": 0}))
        return results

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/drivers", response_model=List[Dict[str, Any]])
async def get_drivers():
    try:
        drivers = list(db.drivers.find({}, {'_id': 0}))
        return drivers
    except Exception as e:
        logger.error(f"Błąd podczas pobierania danych o kierowcach: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/teams", response_model=List[Dict[str, Any]])
async def get_teams():
    try:
        teams = list(db.teams.find({}, {'_id': 0}))
        return teams
    except Exception as e:
        logger.error(f"Błąd podczas pobierania danych o zespołach: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/refresh", response_model=Dict[str, Any])
async def manual_refresh(background_tasks: BackgroundTasks):
    background_tasks.add_task(refresh_data)
    return {"message": "Odświeżanie danych rozpoczęte w tle"}

@app.get("/api/formula1/data")
async def get_formula1_data(collection: str, limit: Optional[int] = 100):
    client = MongoClient("mongodb://mongo:27017/")
    db = client["formula1"]
    data = list(db[collection].find({}, {"_id": 0}).limit(limit))
    return data    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)