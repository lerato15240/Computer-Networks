import logging
import time
import ssl
import socket
import base64

class POP3Client:
    def __init__(self, host, username, password, port=995):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.socket = None
        self.authenticated = False

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket = ssl.wrap_socket(self.socket)
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
        if response.startswith('+OK'):
            self.authenticated = True

    def list_messages(self):
        response = self.send_command('LIST')
        return response.split('\n')[1:-2]  # Exclude the first and last line

    def close(self):
        self.send_command('QUIT')
        self.socket.close()

class SMTPClient:
    def __init__(self, host, username, password, monitor_email, port=587, timeout=20):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.monitor_email = monitor_email
        self.timeout = timeout
        self.socket = None

    # Other methods remain unchanged

    def send_email(self, recipient, subject, body):
        try:
            self.connect()
            self.send_command(f'EHLO {self.host}')
            self.send_command('STARTTLS')

            self.socket = ssl.wrap_socket(self.socket)
            self.send_command(f'EHLO {self.host}')
            self.send_command('AUTH LOGIN')
            self.send_command(base64.b64encode(self.username.encode()).decode())
            self.send_command(base64.b64encode(self.password.encode()).decode())

            self.send_command(f'MAIL FROM: <{self.username}>')
            self.send_command(f'RCPT TO: <{recipient}>')
            self.send_command('DATA')

            # Construct the email message
            email_message = f"From: {self.username}\r\n"
            email_message += f"To: {recipient}\r\n"
            email_message += f"Subject: {subject}\r\n\r\n"
            email_message += body

            self.send_command(email_message)
            self.send_command('.')
            self.send_command('QUIT')

            logging.info("Email sent successfully.")
        except Exception as e:
            logging.error("Error sending email: %s", e)

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    pop3_username = 'lerato15278@gmail.com'
    pop3_password = 'buvk noyj ibns clwh'
    smtp_username = 'lerato15278@gmail.com'  # Replace with your SMTP username
    smtp_password = 'buvk noyj ibns clwh'  # Replace with your SMTP password

    pop3_client = POP3Client('pop.gmail.com', pop3_username, pop3_password)
    smtp_client = SMTPClient('smtp.gmail.com', smtp_username, smtp_password, monitor_email='lerato15278@gmail.com')

    while True:
        try:
            logging.info("Connecting to POP3 server...")
            pop3_client.connect()
            logging.info("Connected to POP3 server.")
            pop3_client.login()
            if pop3_client.authenticated:
                logging.info("Successfully authenticated.")
                messages = pop3_client.list_messages()
                messages.reverse()  # Reverse the order of messages
                logging.info("Number of messages: %d", len(messages))

                for message in messages:
                    message_id, size = message.split()
                    response = pop3_client.send_command(f'RETR {message_id}')
                    response_lines = response.split('\r\n')
                    try:
                        headers_end_index = response_lines.index('')
                        headers = response_lines[:headers_end_index]
                        body = '\r\n'.join(response_lines[headers_end_index+1:])  # Skip the empty line and join the rest as body
                    except ValueError:
                        # If empty line is not found, assume entire response is headers and no body
                        headers = response_lines
                        body = ''

                    bcc_header = next((header for header in headers if header.lower().startswith('bcc:')), None)

                    if bcc_header:
                        print("Email with Bcc:")
                        print('\r\n'.join(headers))
                        print('\r\n\r\n')
                        print("body:", body)
                        sender = next(header for header in headers if header.lower().startswith('from:')).split('<')[1].split('>')[0]

                        subject = next(header for header in headers if header.lower().startswith('subject:')).split(': ', 1)[1]

                        warning_subject = f'[BCC Warning] {subject}'

                        warning_body = f"You received this email as a blind carbon copied recipient. Be cautious when replying to all."

                        smtp_client.connect()

                        smtp_client.send_email(pop3_username, warning_subject, warning_body)

                        smtp_client.close()

                        logging.info("Warning email sent.")
                        break

            else:
                logging.error("Authentication failed.")

            pop3_client.close()

        except Exception as e:
            logging.error("Error: %s", e)

        time.sleep(10)

if __name__ == "__main__":
    main()
