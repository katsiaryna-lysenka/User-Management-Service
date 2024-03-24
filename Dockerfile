FROM python:3.10.12

WORKDIR /fastapi-app

COPY . .

RUN pip install -r requirements.txt

COPY ./app ./app

CMD ["python", "./app/main.py"]