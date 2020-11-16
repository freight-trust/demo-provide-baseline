FROM python:3.8-alpine

WORKDIR /system-tests

RUN apk update && apk add make bash nmap

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY ./ ./

ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT [ "docker/entrypoint.sh" ]
