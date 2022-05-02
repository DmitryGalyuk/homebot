FROM python:3.8-slim AS bot

ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100

RUN apt-get update
RUN apt-get install -y python3 python3-pip python-dev build-essential python3-venv

ARG t

ADD ./requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

RUN mkdir -p /src
ADD ./src /src
WORKDIR /src
RUN chmod +x /src/*.py

# Env vars
ENV TELEGRAM_TOKEN ${TELEGRAM_TOKEN}
ENV TORRENT_HOST ${TORRENT_HOST}
ENV TORRENT_USERNAME ${TORRENT_USERNAME}
ENV TORRENT_PASSWORD ${TORRENT_PASSWORD}
ENV TELEGRAM_USER_ID ${TELEGRAM_USER_ID}

CMD python3 /src/main.py