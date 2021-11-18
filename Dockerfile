FROM ghcr.io/gi0baro/poetry-bin:3.9 as builder

COPY pyproject.toml .
COPY poetry.lock .
RUN poetry install --no-dev

FROM docker.io/library/node:16 as css

COPY fe/css wrk/fe/css
COPY tfstater/templates wrk/tfstater/templates
WORKDIR /wrk/fe/css

ENV NODE_ENV production

RUN npm ci --also=dev && npx tailwindcss -i src/tailwind.css -c tailwind.config.js -o dist/main.css --minify

FROM docker.io/library/node:16 as components

COPY fe/components wrk
WORKDIR /wrk

RUN npm ci && npm run buildwc

FROM docker.io/library/python:3.9-slim

COPY --from=builder /.venv /.venv
ENV PATH /.venv/bin:$PATH

WORKDIR /app
COPY tfstater app
COPY --from=css /wrk/fe/css/dist/main.css app/static/bundled/main.css
COPY --from=components /wrk/dist/components.umd.min.js app/static/bundled/components.min.js

EXPOSE 8000

ENTRYPOINT [ "gunicorn" ]
CMD [ "app:app", "-k", "emmett.asgi.workers.EmmettWorker", "-b", "0.0.0.0:8000", "-w", "2", "--access-logfile", "-" ]
