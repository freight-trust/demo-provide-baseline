FROM python:3.8-alpine

RUN apk update && apk add bash make g++ gcc nmap

WORKDIR /contract-event-listener

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY ./ ./

ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["/contract-event-listener/docker/entrypoint.sh"]
