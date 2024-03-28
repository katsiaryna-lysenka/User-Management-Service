FROM python:3.10.12-slim AS builder

COPY pyproject.toml poetry.lock ./

WORKDIR /app

RUN apt-get update &&  \
    apt-get install -y --no-install-recommends gcc && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --only main

COPY . /app

EXPOSE 5000

CMD ["python3", "main.py"]
