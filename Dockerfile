FROM python:3.9.6-alpine
LABEL authors="wiky"
WORKDIR /app
COPY . /app
RUN apk add curl gdb
RUN pip3 install -r requirements.txt
EXPOSE 5000
CMD ["python3", "/app/main.py"]