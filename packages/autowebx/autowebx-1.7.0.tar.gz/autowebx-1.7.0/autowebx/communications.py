from multiprocessing.connection import Listener
from multiprocessing.connection import Client
from threading import Lock

__lock = Lock()


def send(msg):
    with Listener(('localhost', 3011)) as listener:
        with listener.accept() as conn:
            conn.send(msg)


def receive():
    with __lock:
        try:
            with Client(('localhost', 3011)) as conn:
                return conn.recv()
        except ConnectionRefusedError:
            raise ConnectionRefusedError("Run the sender first")
