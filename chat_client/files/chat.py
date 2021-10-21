import tkinter as tk
from tkinter import simpledialog
import threading
import socket
import time
import ctypes
import json

HOST = "127.0.0.1"
PORT = 43333

# Username input found at: https://djangocentral.com/creating-user-input-dialog/
ROOT = tk.Tk()

ROOT.withdraw()

# Tkinter chatbox/functions found in lesson 1/ lesson 10


class Chat(tk.Frame):
    def __init__(self, parent, username):
        super().__init__(parent, padx=20)
        self.generate_widgets()
        self.bind_widgets()
        self.pack()
        self.username = username

    def generate_widgets(self):
        self.chat_label = tk.Label(
            self,
            text="Chat tjänsten",
            font=('Roboto', 24),
            pady=10
        )
        self.chat_label.grid(
            row=0,
            columnspan=5
        )

        self.chat_entry = tk.Entry(
            self,
            font=("Roboto", 14)
        )
        self.chat_entry.grid(
            row=2,
            column=0,
            sticky=tk.EW,
            columnspan=4,
            pady=20
        )

        self.chat_button = tk.Button(
            self,
            text="Send message"
        )
        self.chat_button.grid(
            row=2,
            column=4,
            sticky=tk.EW,
            padx=(20, 0)
        )

        self.chat_text = tk.Text(
            self,
            font=("Roboto", 14),
            state=tk.DISABLED
        )

        self.chat_text.grid(
            row=1,
            sticky=tk.EW,
            columnspan=5,
            column=0
        )

    def bind_widgets(self):
        self.chat_entry.bind("<Return>", self.submit_chat_message)
        self.chat_button.bind("<Return>", self.submit_chat_message,)
        self.chat_button.bind("<Button-1>", self.submit_chat_message, "+")

    def submit_chat_message(self, event=None):
        text = self.chat_entry.get()
        if text == "":
            return
        self.socket_client.send_data(self.username, text)

        self.clear_entry_text()

    def add_text(self, username, text):
        self.chat_text.configure(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f'{username}: {text}\n')
        self.chat_text.configure(state=tk.DISABLED)

    def recv_text(self, text):
        self.chat_text.configure(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f'{text}\n')
        self.chat_text.configure(state=tk.DISABLED)

    def clear_entry_text(self):
        self.chat_entry.delete(0, tk.END)

    def set_socket(self, socket):
        self.socket_client = socket


class MainWindow(tk.Tk):
    def __init__(self, parent):
        # Asks user for their username
        username = simpledialog.askstring(title="Chat tjänsten", prompt="Vad är ditt användarnamn?:")
        super().__init__(parent)

        # Init
        self.chat = Chat(self, username)
        self.socket_client = SocketClient(self, username)


class SocketClient(MainWindow):
    def __init__(self, mw, username):
        # Setup Receive Handler
        self.recv_handler = mw.chat.recv_text
        self.mw = mw

        # Connect Socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))
        self.socket.settimeout(10)

        # Send Username
        if self.socket.recv(1024) != b"user":
            self.error("Server didn't ask for username.")
        self.socket.send(username.encode("utf-8"))

        # Start Receive Loop
        self.recv_thread_stop = False
        self.recv_thread = threading.Thread(target=self.recv_loop, args=())
        self.recv_thread.start()

        # Start Keep Alive Loop
        self.keep_alive_thread_stop = False
        self.keep_alive_thread = threading.Thread(target=self.keep_alive, args=())
        self.keep_alive_thread.start()

        # Set Socket On The Chat
        mw.chat.set_socket(self)

    def error(self, text):
        self.mw.chat.chat_text.configure(state=tk.DISABLED)
        self.mw.chat.chat_entry.configure(state=tk.DISABLED)
        self.mw.chat.chat_button.configure(state=tk.DISABLED)
        ctypes.windll.user32.MessageBoxW(0, text, "Critical Socket Connection", 0)
        self.recv_thread_stop = True
        self.keep_alive_thread_stop = True

    def recv_loop(self):
        # Checks server status
        if self.socket.recv(5) != b"ready":
            self.error("Server didn't confirm ready status.")
        while not self.recv_thread_stop:
            try:
                data = self.socket.recv(4096)
                if self.recv_handler and data != b"pong":
                    self.recv_handler(data.decode("utf-8"))
            except:
                self.socket.close()
                break

    def keep_alive(self):
        # Keeps alive and checks if the connections is lost
        self.next_alive = time.time() + 1
        while not self.keep_alive_thread_stop:
            if self.socket._closed:
                self.error("Connection lost.")
                break
            if time.time() < self.next_alive:
                time.sleep(0.1)
                continue
            self.next_alive = time.time() + 5
            self.socket.send(b"ping")

    def send_data(self, username, txt):
        self.socket.send(json.dumps({
            "text": txt
        }).encode("utf-8"))


def main():
    mw = MainWindow(None)
    mw.mainloop()


if __name__ == "__main__":
    main()
