FROM python:3.10.12-slim AS builder

WORKDIR /src

COPY pyproject.toml poetry.lock ./

RUN apt-get update &&  \
    apt-get install -y --no-install-recommends gcc && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --only main

COPY . .

EXPOSE 80

CMD ["python", "/src/app/main.py"]
