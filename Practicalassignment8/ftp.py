import socket
import os
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_command(ftp_socket, command):
    ftp_socket.send(command.encode() + b'\r\n')
    response = ftp_socket.recv(1024).decode()
    logging.info(f"Command: {command.strip()}, Response: {response.strip()}")
    return response

def get_passive_mode_port(response):
    try:
        start = response.find('(') + 1
        end = response.find(')')
        parts = response[start:end].split(',')
        ip = '.'.join(parts[:4])
        port = (int(parts[4]) << 8) + int(parts[5])
        logging.info(f"Parsed PASV response: IP={ip}, Port={port}")
        return ip, port
    except Exception as e:
        logging.error("Error parsing PASV response:", exc_info=e)
        return None, None

def download_file_from_ftp(server, port, username, password, remote_file, local_file):
    ftp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        ftp_socket.connect((server, port))
        logging.info(ftp_socket.recv(1024).decode())

        send_command(ftp_socket, 'USER ' + username)
        send_command(ftp_socket, 'PASS ' + password)

        response = send_command(ftp_socket, 'PASV')
        data_ip, data_port = get_passive_mode_port(response)

        if data_ip is None or data_port is None:
            raise Exception("Failed to enter passive mode.")

        send_command(ftp_socket, 'TYPE I')  # Switch to binary mode

        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.connect((data_ip, data_port))

        response = send_command(ftp_socket, 'RETR ' + remote_file)
        if "550" in response:
            raise Exception(f"Failed to open file: {remote_file}, Response: {response}")

        # Read file contents directly into memory
        file_contents = b''
        while True:
            data = data_socket.recv(1024)
            if not data:
                break
            file_contents += data
        data_socket.close()

        send_command(ftp_socket, 'QUIT')
        logging.info("File downloaded successfully.")

        # Write the contents directly to the protected file
        with open(local_file, 'wb') as f:
            f.write(file_contents)
        logging.info("File updated successfully.")
    except Exception as e:
        logging.error("FTP Error:", exc_info=e)
    finally:
        if ftp_socket:
            ftp_socket.close()

def monitor_file(file_path):
    return os.path.getmtime(file_path)

def main():
    protected_file = "/mnt/c/Users/user/OneDrive/Documents/AAAA/Practicalassignment8/protected_file.txt"
    known_good_file = "/var/ftp/pub/known_good.txt"
    last_modified_time = monitor_file(protected_file)

    while True:
        current_modified_time = monitor_file(protected_file)

        if current_modified_time != last_modified_time:
            logging.info("File modified. Updating from the FTP server...")

            try:
                download_file_from_ftp('127.0.0.1', 21, 'anonymous', '', known_good_file, protected_file)
            except Exception as e:
                logging.error("Error updating file:", exc_info=e)

            last_modified_time = monitor_file(protected_file)

        time.sleep(60)

if __name__ == "__main__":
    main()
