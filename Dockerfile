FROM python:3.10

WORKDIR /app

COPY .git .
COPY GoldyBot ./GoldyBot
COPY pyproject.toml .
COPY docker_stuff .

RUN pip install .
RUN git submodule update --init --recursive

ENV DOCKER true

ENV WAIT_VERSION 2.7.2
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait

CMD ["/bin/sh", "./run.sh"]