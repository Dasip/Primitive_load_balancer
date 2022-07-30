import logging
import sys
import threading
import time
import requests

from flask import Flask, request
from environs import Env


class Service():

    def __init__(self, ip, port):

        self.ip = ip
        self.port = port
        self.alive = False

        self.requests_in_process = 0

        self.logger = logging.getLogger(str(port))
        self.logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(f"logs/{self.port}.log")
        file_handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
        self.logger.addHandler(file_handler)

        self.thread = threading.Thread(target=self.start_logger)
        self.thread.start()

        self.app_thread = None

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

        @self.app.route('/shutdown', methods=['GET'])
        def stop_it_already():
            shutdown_func = request.environ.get('werkzeug.server.shutdown')
            if shutdown_func is None:
                raise RuntimeError('Not running werkzeug')
            shutdown_func()
            return "Shutting down..."

    def start_logger(self):
        self.alive = True
        while self.alive:
            time.sleep(10)
            self.logger.warning(f"Запросов в обработке на данный момент: {self.requests_in_process}")

    def complete_request(self):
        time.sleep(11)
        self.requests_in_process -= 1

    def start_app(self):
        self.app_thread = threading.Thread(target=self.app.run, args=(self.ip, self.port))
        self.app_thread.start()

    def startup(self):
        self.start_app()
        sys.exit(1)

    def stop(self):
        self.alive = False
        self.thread.join()
        requests.get(f"http://{self.ip}:{self.port}/shutdown")
        self.app_thread.join()
        print(self.thread, self.app_thread)


if __name__ == "__main__":
    s = Service("127.0.0.1", 8001)
    s.startup()