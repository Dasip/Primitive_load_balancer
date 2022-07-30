import sys
import threading
import time

from requests import *

t1 = None

class ManualTester():

    def __init__(self):
        self.on = False
        self.thread = threading.Thread(target=self.startup)

    def start(self):
        self.thread.start()

    def startup(self):
        self.on = True
        while self.on:
            response = get("http://127.0.0.1:5000")
            #print(response, response.text)

    def shutdown(self):
        self.on = False
        self.thread.join()
        print(self.thread)

