import logging
import sys
import threading
import time

from flask import Flask
from environs import Env


class Service():

    def __init__(self, ip, port):

        self.ip = ip
        self.port = port

        self.requests_in_process = 0

        self.logger = logging.getLogger(str(port))
        self.logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(f"logs/{self.port}.log")
        file_handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
        self.logger.addHandler(file_handler)

        thread = threading.Thread(target=self.start_logger)
        thread.start()

        self.app = Flask(str(port))

        @self.app.route("/", methods=["POST", "GET"])
        def process():
            self.requests_in_process += 1
            t3 = threading.Thread(target=self.complete_request)
            t3.start()
            return "OK", 200

        @self.app.route("/loadLevel", methods=["GET"])
        def get_request_amount():
            return f"{self.requests_in_process}", 200

    def start_logger(self):
        while True:
            time.sleep(10)
            self.logger.warning(f"Запросов в обработке на данный момент: {self.requests_in_process}")

    def complete_request(self):
        time.sleep(11)
        self.requests_in_process -= 1

    def start_app(self):
        thread = threading.Thread(target=self.app.run, args=(self.ip, self.port))
        thread.start()

    def startup(self):
        self.start_app()
        time.sleep(310)
        sys.exit(1)


if __name__ == "__main__":
    s = Service("127.0.0.1", 8001)
    s.startup()