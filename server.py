import pickle
import socket
import struct
import threading
import pyautogui
import pygame
from io import BytesIO
from PIL import Image
import keyboard


class Server:
    client_socket = 0

    def __init__(self, server_ip='192.168.1.212', server_port=5000):
        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080))
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((server_ip, server_port))
        self.server_socket.listen(1)
        self.conn, _ = self.server_socket.accept()
        self.running = True

        self.server_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_tcp_socket.bind((server_ip, server_port + 1))
        self.server_tcp_socket.listen(5)
        print(f'Server listening on {server_ip}:{server_port}')
        self.client_socket, client_address = self.server_tcp_socket.accept()

        threading.Thread(target=self.keyboard).start()
        #threading.Thread(target=self.mouse).start()

    def receive_image(self):
        try:
            # Receive size of the image data
            img_size_data = self.conn.recv(4)
            if not img_size_data:
                return False
            img_size = int.from_bytes(img_size_data, 'big')

            # Receive the image data
            img_data = b''
            while len(img_data) < img_size:
                packet = self.conn.recv(img_size - len(img_data))
                if not packet:
                    return False
                img_data += packet

            # Process image data
            img = Image.open(BytesIO(img_data))
            img = img.convert('RGB')
            mode = 'RGB'  # Ensuring the mode is 'RGB' for pygame
            size = img.size
            data = img.tobytes()

            # Display image in Pygame
            pygame_surface = pygame.image.fromstring(data, size, mode)
            self.screen.blit(pygame_surface, (0, 0))
            pygame.display.flip()
            return True

        except Exception as e:
            print(f"Error: {e}")
            return False

    def run(self):
        while self.running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            if not self.receive_image():
                self.running = False

        pygame.quit()
        self.server_socket.close()

    def mouse(self):
        while True:
            mouse_pos_x = pyautogui.position().x
            self.client_socket.send(str(mouse_pos_x).encode())
            mouse_pos_y = pyautogui.position().y
            self.client_socket.send(str(mouse_pos_y).encode())

    def keyboard(self):
        def on_key_event(event):
            key = event.name
            self.client_socket.sendall(key.encode())
            print(f'Sent key: {key}')

        print("Press ESC to stop capturing keys.")
        keyboard.on_press(on_key_event)
        keyboard.wait('esc')
# Usage
if __name__ == '__main__':
    receiver = Server()
    receiver.run()
