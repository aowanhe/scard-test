def start_server(self):
    ip = self.ip_input.text()
    port = int(self.port_input.text())

    self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server_socket.bind((ip, port))
    self.server_socket.listen(5)

    self.log_area.append(f"Server started on {ip}:{port}")

    threading.Thread(target=self.accept_clients).start()



def accept_clients(self):
    while True:
        client_socket, client_address = self.server_socket.accept()
        self.client_sockets.append(client_socket)
        self.log_area.append(f"Client connected from {client_address}")
        threading.Thread(target=self.handle_client, args=(client_socket,)).start()


def handle_client(self, client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if data:
                self.log_area.append(f"Received: {data}")
        except ConnectionResetError:
            self.log_area.append("Client disconnected")
            self.client_sockets.remove(client_socket)
            break