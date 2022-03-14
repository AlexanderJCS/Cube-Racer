import threading
import logging
import socket
import time
import pickle

from pyTwistyScrambler import scrambler333

# Init libraries
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S'
)


HEADERSIZE = 10

IP = "192.168.1.12"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))
server_socket.listen(10)

clients = []

# Classes


class Game:
    def __init__(self):
        self.participating_clients = list(clients)

    def start_game(self):
        scramble = scrambler333.get_WCA_scramble()

        for client in self.participating_clients:
            # Send "start game" to clients
            self.send(client, "start game")
            # Send scramble to clients
            self.send(client, scramble)

    def generate_leaderboard(self):
        # Listen until all clients are finished or the time exceeds MAX_TIME constant
        times = {}
        for client in self.participating_clients:
            info = self.recieve(client)

            if not info:
                return

            username = info.get("username")
            user_time = info.get("user_time")
            penalty = info.get("penalty")

            if penalty == "DNF":
                user_time = "DNF"

            elif penalty == "+2":
                user_time += 2

            times[username] = round(user_time, 3) if user_time != "DNF" else "DNF"

        # Send times to client
        for client in clients:
            self.send(client, times)

    def recieve(self, client_socket):
        logging.debug("Recieving message")
        try:
            message_header = client_socket.recv(HEADERSIZE)
            message_length = int(message_header.decode('utf-8').strip())
            return pickle.loads(client_socket.recv(message_length))

        except (ConnectionResetError, ValueError):
            clients.remove(client_socket)
            self.participating_clients.remove(client_socket)
            logging.info("Client disconnected.")

    def send(self, client_socket, message):
        logging.debug(f"Sending message {message}")
        try:
            message = pickle.dumps(message)
            message = f"{len(message):<{HEADERSIZE}}".encode("utf-8") + message
            client_socket.send(message)

        except ConnectionResetError:
            clients.remove(client_socket)
            self.participating_clients.remove(client_socket)
            logging.info("Client disconnected.")


# Functions
def manage_clients():
    logging.info("Waiting for clients to connect")
    while True:
        clientsocket, address = server_socket.accept()

        clients.append(clientsocket)
        logging.info(f"Client connected. {len(clients)} clients connected.")


def main():
    t = threading.Thread(target=manage_clients)
    t.start()

    while True:
        while len(clients) > 1:
            g = Game()
            g.start_game()
            g.generate_leaderboard()
        time.sleep(0.1)


if __name__ == "__main__":
    main()
