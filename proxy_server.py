import socket, sys, yaml, requests, logging
import threading
import time

from manual_tests import start_tester
from target import Service


class LoadBalancer():

    def __init__(self):
        with open("config.yaml", "r") as yml:
            config = yaml.safe_load(yml)

        self.listen_port = int(config["config"]["port"])
        self.ip = config["config"]["ip"]
        self.buffer_size = config["config"]["buffer_size"]
        self.max_connections = config["config"]["max_connections"]
        self.servers = []
        self.working_servers = []
        self.disconnected_servers = []

        self.alive = False

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(f"logs/{config['config']['logfile']}.log")
        file_handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
        self.logger.addHandler(file_handler)

        self.logger.info("Initializing server list...")
        for ip, port in zip(config["server_list"]["server_ip"], config["server_list"]["server_port"]):
            self.servers.append((ip, int(port)))
            self.disconnected_servers.append((ip, int(port)))
            self.logger.info(f"Initialized {ip}:{port}")
        self.logger.info("Server list initialization complete")

        self.logger.info("Initializing socket...")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.ip, self.listen_port))
        self.socket.listen(self.max_connections)
        self.logger.info(f"Socket {self.ip}:{self.listen_port} initialization complete")

    def startup_server(self, server):
        if server in self.servers and server in self.disconnected_servers:
            self.logger.warning(f"Connecting {server[0]}:{server[1]}")
            self.disconnected_servers.remove(server)
            self.working_servers.append(server)

    def startup_all_servers(self):
        self.logger.warning("Setting up all servers on-line...")
        for i in self.servers:
            print(i)
            new_service = Service(i[0], i[1])
            t = threading.Thread(target=new_service.startup)
            t.start()
            self.logger.warning(f"Server {i[0]}:{i[1]} is on-line!")
            time.sleep(0.1)
        self.logger.warning("All servers set on-line")

        self.logger.warning("Connecting all servers...")
        for i in self.servers:
            self.startup_server(i)
        self.logger.warning("All servers connected")

    def disconnect_server(self, server):
        if server in self.servers and server in self.working_servers:
            self.logger.warning(f"Disconnecting {server[0]}:{server[1]}")
            self.working_servers.remove(server)
            self.disconnected_servers.append(server)

    def find_least_loaded_server(self):
        load_lvl = []
        server = self.working_servers[0]
        for i in self.working_servers:
            load_lvl.append(int(requests.get(f"http://{i[0]}:{i[1]}/loadLevel").text))
            if load_lvl[-1] <= min(load_lvl):
                server = i

        self.logger.error(f"Load level: {load_lvl}")
        self.logger.info(f"Least loaded server for connection: {server[0]}:{server[1]} - {min(load_lvl)}")
        return server

    def startup(self):
        self.startup_all_servers()
        self.alive = True
        while self.alive:
            conn, addr = self.socket.accept()
            self.logger.info(f"Accepted a connection: {addr[0]}:{addr[1]}")
            if addr not in self.servers:
                self.logger.info(f"Balancing a request from {addr} onto working servers")
                data = conn.recv(self.buffer_size)
                least_loaded_server = self.find_least_loaded_server()
                #print(least_loaded_server)
                self.connect_the_two(data, conn, addr, least_loaded_server)
        sys.exit(2)

    def connect_the_two(self, data, conn, addr, server):
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_socket.connect(server)
        new_socket.send(data)

        response = new_socket.recv(self.buffer_size)
        conn.send(response)
        conn.close()
        new_socket.close()


if __name__ == "__main__":

    #main()
    f = LoadBalancer()
    t1 = threading.Thread(target=f.startup)
    t2 = threading.Thread(target=start_tester)
    t1.start()
    t2.start()
    time.sleep(5)
    f.disconnect_server(f.working_servers[2])
    time.sleep(5)
    f.startup_server(f.disconnected_servers[0])
    time.sleep(5)
    f.alive = False