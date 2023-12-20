FROM python:3.10-slim-bookworm

WORKDIR /app

COPY GoldyBot ./GoldyBot
COPY pyproject.toml .
COPY docker_stuff .

RUN apt-get update && apt-get install -y git gcc python3-dev
RUN pip install .

ENV DOCKER true

ENV WAIT_VERSION 2.7.2
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait

CMD ["/bin/sh", "./run.sh"]