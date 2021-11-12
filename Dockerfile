FROM ghcr.io/gi0baro/poetry-bin:3.9-slim as builder

RUN apt-get -qq update -y && apt-get -q install -y gcc git

COPY pyproject.toml .
COPY poetry.lock .
RUN poetry install --no-dev

FROM docker.io/library/python:3.9-slim

COPY --from=builder /.venv /.venv
ENV PATH /.venv/bin:$PATH

WORKDIR /app
COPY tfstater app

EXPOSE 8000

ENTRYPOINT [ "emmett" ]
CMD [ "serve", "--no-access-log", "--max-concurrency", "512" ]
