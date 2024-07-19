import pickle
import socket
import struct
import keyboard
import pyautogui
from PIL import ImageGrab
import io
import threading


class Client:
    def __init__(self, server_ip='192.168.1.212', server_port=5000):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_ip, self.server_port))

        self.client_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f'Server listening on {server_ip}:{server_port}')
        self.client_tcp_socket.connect((server_ip, server_port + 1))
        print(f'Connected to server at {server_ip}:{server_port}')

        self.client_mouse_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f'Server listening on {server_ip}:{server_port}')
        self.client_mouse_socket.connect((server_ip, server_port + 2))
        print(f'Connected to server at {server_ip}:{server_port}')

        threading.Thread(target=self.receive_keys).start()
        threading.Thread(target=self.mouse).start()

    def capture_and_send(self):
        screen = ImageGrab.grab()
        img_byte_arr = io.BytesIO()
        screen.save(img_byte_arr, format='PNG')
        img_data = img_byte_arr.getvalue()

        self.client_socket.sendall(len(img_data).to_bytes(4, 'big'))  # Send size first
        self.client_socket.sendall(img_data)  # Then send the actual data

    def receive_keys(self):
        try:
            while True:
                data = self.client_tcp_socket.recv(1024)
                if data:
                    print(f'Received key: {data.decode()}')
                    keyboard.press(data.decode())
                else:
                    break
        except ConnectionError:
            print("Connection to server lost.")
        finally:
            self.client_tcp_socket.close()

    def mouse(self):
        while True:
            data = self.client_mouse_socket.recv(1024).decode('utf-8')
            if not data:
                break
            print(f"Received command: {data}")

            if data == "MOVE":
                x, y = self.client_mouse_socket.recv(1024).decode().split(',')
                print(f"Received command: {x}")
                pyautogui.moveTo(int(x), int(y))
            elif data == "CLICK":
                pyautogui.click()

    def run(self):
        try:
            while True:
                self.capture_and_send()

        except KeyboardInterrupt:
            print("Client stopped.")
        finally:
            self.client_socket.close()

# Usage
if __name__ == '__main__':
    client = Client()
    client.run()





