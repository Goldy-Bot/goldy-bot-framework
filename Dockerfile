FROM python:3.11-slim-bookworm

WORKDIR /app

COPY GoldyBot ./GoldyBot
COPY goldy_bot ./goldy_bot
COPY pyproject.toml .
COPY docker-entrypoint.sh .

RUN apt-get update && apt-get install -y git gcc python3-dev
RUN pip install .

RUN rm -r ./GoldyBot ./goldy_bot ./GoldyBot.egg-info ./build ./pyproject.toml

ENV DOCKER true

ENV WAIT_VERSION 2.7.2
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait

CMD ["/bin/sh", "./docker-entrypoint.sh"]