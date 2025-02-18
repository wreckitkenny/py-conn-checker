import os, logging
from flask import Flask, request
from checker import request_handler, load_config

app = Flask(__name__)
logger = logging.getLogger(os.path.dirname(__file__).split("/")[-1])

@app.route("/ping")
def ping(): return "pong!"

@app.post("/checkConnection")
def check_connection():
    jsonRequest = request.get_json()
    logger.info("Handling a request: {}".format(jsonRequest))
    return request_handler(json_request=jsonRequest)

if __name__ == '__main__':
    log = logging.getLogger('werkzeug')
    log.disabled = True
    load_config("config/logging.yaml")
    app.run(host='0.0.0.0', port=5000)
