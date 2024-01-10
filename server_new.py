import socket

def start_server():
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Get the hostname and port
    host_name = socket.gethostname()
    host = socket.gethostbyname(host_name)
    port = 9999

    # Bind to the port
    server_socket.bind(('localhost', 9999))

    # Listen for incoming connections
    server_socket.listen()

    print(f"Server is listening on {host}:{port}")

    while True:
        # Accept a new connection
        client_socket, address = server_socket.accept()

        # Lists the connection
        print(f"Connection from {address} has been established.")

start_server()
