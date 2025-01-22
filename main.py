from flask import Flask, request
from k8s.handler import request_handler

app = Flask(__name__)

@app.route("/ping")
def ping(): return "pong!"

@app.post("/checkConnection")
def check_connection():
    jsonRequest = request.get_json()
    return request_handler(json_request=jsonRequest)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
