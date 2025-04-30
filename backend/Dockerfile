FROM python:3.11-slim

WORKDIR /app

# Instalujemy git do klonowania openf1
RUN apt-get update 
RUN apt-get install -y git

# Klonujemy openf1 przed kopiowaniem własnych plików (żeby nie został nadpisany)
RUN git clone https://github.com/br-g/openf1.git

# Instalujemy wymagania i openf1 jako edytowalną paczkę
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e ./openf1

# Kopiujemy pliki projektu (po zainstalowaniu openf1!)
COPY . .


RUN chmod +x /app/start.sh

EXPOSE 8000


CMD ["/bin/bash", "/app/start.sh"]
