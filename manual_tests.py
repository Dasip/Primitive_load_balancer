import sys
import threading
import time

from requests import *


class ManualTester():

    def __init__(self):
        self.on = False

    def startup(self):
        self.on = True
        while self.on:
            response = get("http://127.0.0.1:5000")
            print(response, response.text)

    def shutdown(self):
        self.on = False


def start_tester():
    tester = ManualTester()
    t1 = threading.Thread(target=tester.startup)
    t1.start()
    time.sleep(15)
    tester.shutdown()
    sys.exit(1)


if __name__ == "__main__":
    start_tester()