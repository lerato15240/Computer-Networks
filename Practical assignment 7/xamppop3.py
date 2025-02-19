import socket
import time

class POP3Client:
    def __init__(self, host, username, password, port=110):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.receive_response()

    def receive_response(self):
        return self.socket.recv(4096).decode()

    def send_command(self, command):
        self.socket.sendall(command.encode() + b'\r\n')
        return self.receive_response()

    def login(self):
        self.send_command(f'USER {self.username}')
        response = self.send_command(f'PASS {self.password}')
        return response.startswith('+OK')

    def list_messages(self):
        response = self.send_command('LIST')
        return response.split('\n')[1:-2]  # Exclude the first and last line

    def retrieve_message(self, message_id):
        response = self.send_command(f'RETR {message_id}')
        return response

    def close(self):
        self.send_command('QUIT')
        self.socket.close()

class SMTPClient:
    def __init__(self, host, port=25):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.receive_response()

    def receive_response(self):
        return self.socket.recv(4096).decode()

    def send_command(self, command):
        self.socket.sendall(command.encode() + b'\r\n')
        return self.receive_response()

    def login(self):
        response = self.send_command(f'HELO {self.host}')
        return response.startswith('250')

    def send_email(self, sender, recipient, subject, body):
        self.send_command(f'MAIL FROM:<{sender}>')
        self.send_command(f'RCPT TO:<{recipient}>')
        self.send_command('DATA')
        self.send_command(f'Subject: {subject}')
        self.send_command('')
        self.send_command(body)
        self.send_command('.')
        self.send_command('QUIT')

    def close(self):
        self.socket.close()

def main():
    pop3_client = POP3Client('pop.gmail.com', 'lerato15278@gmail.com', 'xrnd ixnh bjdi jmsl')
    smtp_client = SMTPClient('127.0.0.1')  # Assuming Mercury Mail SMTP is running on localhost

    try:
        while True:
            try:
                print("Connecting to POP3 server...")
                pop3_client.connect()
                print("Connected to POP3 server.")
                if pop3_client.login():
                    print("Successfully authenticated.")
                    messages = pop3_client.list_messages()
                    print("Number of messages:", len(messages))
                    
                    for message_id in messages:
                        email = pop3_client.retrieve_message(message_id.split()[0])
                        if 'BCC:' in email:
                            # Send warning email
                            smtp_client.connect()
                            if smtp_client.login():
                                smtp_client.send_email('lerato15278@gmail.com', 'lerato15278@gmail.com', '[BCC Warning] Blind Copy Detected', email)
                                smtp_client.close()
                                print("Warning email sent.")
                            else:
                                print("SMTP authentication failed.")
                        
                    pop3_client.close()
                else:
                    print("POP3 authentication failed.")

            except Exception as e:
                print(f"Error: {e}")

            time.sleep(10)

    except KeyboardInterrupt:
        print("Program interrupted by user. Cleaning up...")
        pop3_client.close()
        smtp_client.close()
        print("Exiting program.")


if __name__ == "__main__":
    main()
