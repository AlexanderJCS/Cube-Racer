import socket
import pickle
import time
import threading
from tkinter import *

import pygame

# Init pygame
pygame.mixer.init()

# Connect to server

while True:
    IP = input("IP: ")
    PORT = int(input("PORT: "))
    USERNAME = input("USRENAME: ")

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP, PORT))
        print("Successfully connected. Please check other window.")
        break

    except IOError:
        print("Could not connect to server.")


# Main GUI

tk = Tk()
tk.geometry = "500x400"
tk.title = "Cube Racer"

scramble_label = Label(tk, text="Scramble: ", font=("Segoe", 16))
scramble_label.grid(row=1, column=1)

text_box = Text(tk, height=5, width=32, font="Segoe, 16")
text_box.grid(row=2, column=1)

entry_box = Entry(tk, width=10, font=("Segoe", 16))
entry_box.grid(row=3, column=1)

# Constants
HEADERSIZE = 10


# Classes
class Game:
    def __init__(self):
        self.penalty = None
        self.user_time = None

    def run_game(self):
        try:
            while True:
                self.listen_for_game_start()
                self.inspection()
                self.time_solve()
                self.send_time()
                self.recieve_leaderboard()

        except RuntimeError:
            print("GUI closed by client.")

    def inspection(self):
        while not entry_box.get():
            time.sleep(0.02)
        entry_box.delete(0, END)

        for seconds in range(17 * 10):
            if entry_box.get():
                break

            entry_box.delete(0, END)
            if seconds < 15 * 10:
                update_widget(text_box, f"Inspection:\n{(seconds + 1) / 10}")

            if seconds == 8 * 10:
                playsound("8.mp3")

            elif seconds == 12 * 10:
                playsound("12.mp3")

            elif seconds == 15 * 10:
                playsound("plus2.mp3")

            elif seconds > 15 * 10:
                self.penalty = "+2"
                update_widget(text_box, "+2")

            time.sleep(1 / 10)

        else:
            self.penalty = "DNF"
            playsound("dnf.mp3")
            update_widget(text_box, "DNF")

    def time_solve(self):
        if self.penalty == "DNF":
            return

        entry_box.delete(0, END)
        start_time = time.time()
        update_widget(text_box, "Timing solve...")
        scramble_label.config(text="Scramble: ")

        while not entry_box.get():
            time.sleep(0.005)
            update_widget(text_box, round(time.time() - start_time, 1))

        entry_box.delete(0, END)
        end_time = time.time()
        self.user_time = end_time - start_time

        update_widget(text_box, f"Time: "
                                f"{round(self.user_time, 3) if self.penalty != '+2' else round(self.user_time + 2, 3)}"
                                f"\nWaiting for opponents")

    def send_time(self):
        send(USERNAME)
        send(self.user_time)
        send(self.penalty)

    @staticmethod
    def recieve_leaderboard():
        leaderboard = recieve()
        text_box.delete("1.0", END)

        for username in leaderboard:
            text_box.insert(END, f"{username}: {leaderboard[username]}\n")

        time.sleep(3)

    @staticmethod
    def listen_for_game_start():
        while True:
            start = recieve()
            if start == "start game":
                break

        scramble = recieve()
        scramble_label['text'] = f"Scramble: {scramble}"


# Functions
def recieve():
    message_header = client_socket.recv(HEADERSIZE)
    message_length = int(message_header.decode('utf-8').strip())
    return pickle.loads(client_socket.recv(message_length))


def send(message):
    message = pickle.dumps(message)
    message = f"{len(message):<{HEADERSIZE}}".encode("utf-8") + message
    client_socket.send(message)


def update_widget(widget, text):
    widget.delete("1.0", END)
    widget.insert(END, text)


def playsound(file):
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()


def main():
    g = Game()
    t = threading.Thread(target=g.run_game)
    t.start()

    tk.mainloop()


if __name__ == "__main__":
    main()
