#!/bin/bash

echo "Oczekiwanie na dostępność MongoDB..."
# Czekanie na MongoDB
sleep 5

echo "Inicjalizacja bazy danych..."
python init_db.py

echo "Uruchamianie API..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload