FROM tiangolo/uvicorn-gunicorn:python3.8-slim

COPY ./app /app
COPY ./app/schema.yaml /
WORKDIR /app
RUN python3 -m pip install -r requirements.txt
WORKDIR /
