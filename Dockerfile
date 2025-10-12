FROM python:3.13

WORKDIR /app

COPY microservice microservice
COPY requirements.txt ./
COPY google-credentials.json google-credentials.json

RUN apt-get install \
    && pip install -r requirements.txt 

CMD python3 microservice/main.py