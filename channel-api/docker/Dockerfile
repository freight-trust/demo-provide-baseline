FROM python:3.8

WORKDIR /channel-api

COPY ./docker ./docker

RUN docker/install-base.sh

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY ./package* ./

RUN npm ci

COPY ./ ./

ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["./docker/entrypoint.sh"]
