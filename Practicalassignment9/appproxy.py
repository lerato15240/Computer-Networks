import socket
import threading
import base64
import re

# Configuration
PROXY_HOST = 'localhost'
PROXY_PORT = 55555
REAL_POP3_SERVER = ''
REAL_POP3_PORT = 110
PROXY_USER = ''
PROXY_PASS = ''
REAL_USER = ''
REAL_PASS = ''
CONFIDENTIAL_KEYWORD = 'Confidential'

# Function to log messages
def log(message):
    print(f"[LOG] {message}")

# Function to replace confidential emails
def replace_confidential_email(email_data):
    replacement_email = (
        "From: test@example.com\r\n"
        "Subject: Just testing\r\n"
        "\r\n"
        "replacing a confidential message.\r\n"
    )
    return replacement_email.encode()

# Function to insert handled by line
def insert_handled_by(email_data, username):
    handled_by_line = f"\r\nHandled by {username}\r\n"
    email_lines = email_data.split(b'\r\n')
    for i in range(len(email_lines)):
        if email_lines[i].startswith(b'From:'):
            email_lines.insert(i + 1, handled_by_line.encode())
            break
    return b'\r\n'.join(email_lines)

# Function to handle client connections
def handle_client(client_socket):
    try:
        # Connect to the real POP3 server
        real_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        real_socket.connect((REAL_POP3_SERVER, REAL_POP3_PORT))
        log("Connected to real POP3 server")

        # Relay server greeting to client
        server_greeting = real_socket.recv(1024)
        client_socket.send(server_greeting)

        # Perform client authentication
        authenticated = False
        while not authenticated:
            client_data = client_socket.recv(1024).decode()
            if client_data.startswith('USER'):
                username = client_data.split()[1]
                log(f"Client username: {username}")
                if username == PROXY_USER:
                    client_socket.send(b"+OK User accepted\r\n")
                else:
                    client_socket.send(b"-ERR Invalid user\r\n")
            elif client_data.startswith('PASS'):
                password = client_data.split()[1]
                if password == PROXY_PASS:
                    log("Client authenticated successfully")
                    client_socket.send(b"+OK Password accepted\r\n")
                    authenticated = True
                else:
                    client_socket.send(b"-ERR Invalid password\r\n")

        # Authenticate to the real POP3 server
        real_socket.sendall(f"USER {REAL_USER}\r\n".encode())
        real_socket.recv(1024)
        real_socket.sendall(f"PASS {REAL_PASS}\r\n".encode())
        real_socket.recv(1024)

        # Relay commands and responses between client and real server
        while True:
            client_data = client_socket.recv(1024)
            if not client_data:
                break

            command = client_data.decode().strip().split()[0]

            # Handle RETR command for confidential emails and inserting handled by line
            if command.upper() == 'RETR':
                real_socket.sendall(client_data)
                response = real_socket.recv(4096)
                email_data = response

                # Read entire email data
                while True:
                    part = real_socket.recv(4096)
                    email_data += part
                    if b'\r\n.\r\n' in part:
                        break

                email_content = email_data.decode()
                if CONFIDENTIAL_KEYWORD in email_content:
                    log("Confidential email detected and replaced")
                    email_data = replace_confidential_email(email_content)

                email_data = insert_handled_by(email_data, PROXY_USER)
                client_socket.send(email_data)
            else:
                real_socket.sendall(client_data)
                response = real_socket.recv(4096)
                client_socket.send(response)

        real_socket.close()
    except Exception as e:
        log(f"Error: {e}")
    finally:
        client_socket.close()
        log("Client disconnected")

# Function to start the proxy server
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((PROXY_HOST, PROXY_PORT))
    server_socket.listen(5)
    log(f"Proxy server listening on {PROXY_HOST}:{PROXY_PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        log(f"Accepted connection from {addr[0]}:{addr[1]}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()
