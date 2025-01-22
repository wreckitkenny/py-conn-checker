FROM python:3.9.6-alpine
LABEL authors="wiky"
WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "main.py"]