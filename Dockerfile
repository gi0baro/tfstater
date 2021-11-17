FROM ghcr.io/gi0baro/poetry-bin:3.9-slim as builder

RUN apt-get -qq update -y && apt-get -q install -y gcc git

COPY pyproject.toml .
COPY poetry.lock .
RUN poetry install --no-dev

FROM docker.io/library/node:16 as css

COPY fe/css wrk
WORKDIR /wrk

ENV NODE_ENV production

RUN npm ci && npx tailwindcss -i src/tailwind.css -c tailwind.config.js -o dist/main.css --minify

FROM docker.io/library/node:16 as components

COPY fe/components wrk
WORKDIR /wrk

RUN npm ci && npm run buildwc

FROM docker.io/library/python:3.9-slim

COPY --from=builder /.venv /.venv
ENV PATH /.venv/bin:$PATH

WORKDIR /app
COPY tfstater app
COPY --from=css /wrk/dist/main.css app/static/bundled/main.css
COPY --from=components /wrk/dist/components.umd.min.js app/static/bundled/components.min.js

EXPOSE 8000

ENTRYPOINT [ "gunicorn" ]
CMD [ "app:app", "-k", "emmett.asgi.workers.EmmettWorker", "-b", "0.0.0.0:8000", "-w", "2", "--access-logfile", "-" ]
