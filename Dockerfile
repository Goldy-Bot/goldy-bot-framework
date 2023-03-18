FROM python:3.8.9

WORKDIR /app

COPY GoldyBot ./GoldyBot
COPY pyproject.toml .
COPY docker_stuff/run.sh .
COPY docker_stuff/cli.py .
COPY docker_stuff/run.py .

RUN pip install .

ENV WAIT_VERSION 2.7.2
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait

CMD ["/bin/sh", "./run.sh"]