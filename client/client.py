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
REFRESH = 10
WAITING = "Waiting for new round to start."


# Classes
class Game:
    def __init__(self):
        self.penalty = None
        self.user_time = None
        self.only_scramble = False

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

    def listen_for_game_start(self):
        if not self.only_scramble:  # If the program is instructed to listen for an incoming message "game start"
            while True:
                start = recieve()
                if start == "start game":
                    if text_box.get(1.0, "end-1c") == WAITING:
                        update_widget(text_box, "Press any key to start inspection.")
                    break

        # Recieve and display the scramble
        scramble = recieve()
        scramble_label['text'] = f"Scramble: {scramble}"
        self.only_scramble = False

    def inspection(self):
        # Wait for client to start inspection
        while not entry_box.get():
            time.sleep(0.02)
        entry_box.delete(0, END)

        # When client started inspection, count down from 17
        for seconds in range(17 * REFRESH):
            if entry_box.get():
                break

            entry_box.delete(0, END)
            if seconds < 15 * REFRESH:
                update_widget(text_box, f"Inspection:\n{(seconds + 1) / 10}")

            # Playsound if inspection is at 8, 12, or 15
            for i in [i * REFRESH for i in (8, 12, 15)]:
                if seconds == i:
                    playsound(f"{int(i / REFRESH)}.mp3")

            # Display +2 if the user has a penalty of +2
            if seconds >= 15 * REFRESH:
                self.penalty = "+2"
                update_widget(text_box, "+2")

            time.sleep(1 / REFRESH)

        else:  # If the penalty is a DNF
            self.penalty = "DNF"
            playsound("dnf.mp3")
            update_widget(text_box, "DNF")

    def time_solve(self):  # Times the solve
        if self.penalty == "DNF":
            return

        entry_box.delete(0, END)  # Clear entry box
        start_time = time.time()  # Start timer
        scramble_label.config(text="Scramble: ")  # Reset scramble so user can't reverse the scramble

        # Wait 3 seconds before the user can stop timer to prevent holding down a button and stopping immediately
        for _ in range(3 * REFRESH):
            update_widget(text_box, round(time.time() - start_time, 1))
            time.sleep(1 / REFRESH)
        entry_box.delete(0, END)

        # Wait for timer to be stopped
        while not entry_box.get():
            time.sleep(0.005)
            update_widget(text_box, round(time.time() - start_time, 1))

        entry_box.delete(0, END)

        # Calculate final time
        end_time = time.time()
        self.user_time = end_time - start_time

        update_widget(text_box, f"Time: "
                                f"{round(self.user_time, 3) if self.penalty != '+2' else round(self.user_time + 2, 3)}"
                                f"\nWaiting for opponents")

    def send_time(self):  # Sends important information such as username, time, and penalty to the server
        send({"username": USERNAME, "user_time": self.user_time, "penalty": self.penalty})

    def recieve_leaderboard(self):  # Recieves the leaderboard to be shown on the client's screen
        leaderboard = recieve()

        if leaderboard == "start game":
            self.only_scramble = True
            return

        text_box.delete("1.0", END)

        for username in leaderboard:
            text_box.insert(END, f"{username}: {leaderboard[username]}\n")


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
    update_widget(text_box, WAITING)
    g = Game()
    t = threading.Thread(target=g.run_game)
    t.start()

    tk.mainloop()


if __name__ == "__main__":
    main()
