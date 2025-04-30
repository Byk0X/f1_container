FROM python:3.11-slim

WORKDIR /app

# install git
RUN apt-get update 
RUN apt-get install -y git

RUN git clone https://github.com/br-g/openf1.git

# install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e ./openf1

# copy files
COPY . .


RUN chmod +x /app/start.sh

EXPOSE 8000


CMD ["/bin/bash", "/app/start.sh"]
