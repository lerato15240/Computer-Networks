import ssl
import socket
import time
import logging
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
        context = ssl.create_default_context()
        self.socket = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=self.host)
        self.socket.connect((self.host, self.port))
        self.receive_response()

    def receive_response(self):
        response = b''
        last_line = b''
        while True:
            chunk = self.socket.recv(4096)
            if not chunk:
                break
            response += chunk
            if b'\r\n' in chunk:
                break
        return response.decode()

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
        lines = response.split('\n')
        if lines[0].startswith('+OK'):
            lines = lines[1:]
        return [line.strip() for line in lines if line.strip() and line.strip() != '.']

    def close(self):
        self.send_command('QUIT')
        self.socket.close()

class SMTPClient:
    def __init__(self, host, username, password, port=587, timeout=60):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.timeout)
        self.socket.connect((self.host, self.port))
        self.receive_response()

    def receive_response(self):
        return self.socket.recv(4096).decode()

    def send_command(self, command):
        self.socket.sendall(command.encode() + b'\r\n')
        return self.receive_response()

    def send_email(self, recipient, subject, body):
        try:
            
            self.send_command('EHLO smtp.gmail.com')
            self.send_command('STARTTLS')
            context = ssl.create_default_context()
            self.socket = context.wrap_socket(self.socket, server_hostname=self.host)
            self.send_command(f'EHLO smtp.gmail.com')
            self.send_command(f'AUTH LOGIN')
            self.send_command(base64.b64encode(self.username.encode()).decode())
            self.send_command(base64.b64encode(self.password.encode()).decode())
            # Construct the email message
            email_message = f"From: {self.username}\r\n"
            email_message += f"To: {recipient}\r\n"
            email_message += f"Subject: {subject}\r\n\r\n"
            email_message += body

            self.send_command(f'mail from: <{self.username}>')
        
            self.send_command(f'rcpt to: <{recipient}>')
        
            self.send_command('data')
            
            # Send the email message
            self.socket.sendall(email_message.encode())
            
            self.send_command('.')   
            
            self.send_command('quit')
            
            logging.info("Email sent successfully.")
        except Exception as e:
            self.send_command('.') 
            self.send_command('quit')
            logging.error("Error sending email: %s", e)

    def close(self):
        self.socket.close()

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    pop3_username = 'lerato15278@gmail.com'
    pop3_password = 'buvk noyj ibns clwh'
    smtp_username = 'lerato15278@gmail.com' 
    smtp_password = 'buvk noyj ibns clwh'
    #pop3_username = input("Enter your email address: ")
    #pop3_password = input("Enter your  password: ")
    #smtp_username = pop3_username
    #smtp_password = pop3_password 
  
    
    pop3_client = POP3Client('pop.gmail.com', pop3_username, pop3_password)
    smtp_client = SMTPClient('smtp.gmail.com', smtp_username, smtp_password)

    while True:
        try:
            logging.info("Connecting to POP3 server...")
            pop3_client.connect()
            logging.info("Connected to POP3 server.")
            pop3_client.login()
            if pop3_client.authenticated:
                logging.info("Successfully authenticated.")
                messages = pop3_client.list_messages()
                #messages.reverse()  # Reverse the order of messages
                logging.info("Number of messages: %d", len(messages))
                
                for message in messages:
                        try:
                            message_id, size = message.split()
                        except ValueError:
                            logging.error("Error unpacking message: %s", message)
                            continue
                        response = pop3_client.send_command(f'RETR {message_id}')
                        email_data = pop3_client.receive_response()
                        
                        header = email_data

                        # Now email_content contains the entire email content
                        #print("Email Headers:")
                        print(email_data)
                         
                        

                        if 'to:' not in header.lower() and 'cc:' not in header.lower():

                            subject=''
                            subject_line = [line for line in header.split('\n') if line.lower().startswith('subject:')]
                            if subject_line:
                                subject = subject_line[0].split('Subject:', 1)[1].strip()
                                print("Subject:", subject)
                            else:
                                print("Subject not found in header.")                           
                            print("Evidence")
                            
                            warning_subject = f'[BCC Warning] {subject}'
                            warning_body = f"You received this email as a blind carbon copied recipient. Be cautious when replying to all."
                            
                            smtp_client.connect()
                            smtp_client.send_email(pop3_username, warning_subject, warning_body)
                            smtp_client.close()
                            
                            logging.info("Warning email sent.")
                            
                               
            else:
                logging.error("Authentication failed.")
            
            pop3_client.close()

        except Exception as e:
            logging.error("Error: %s", e)

        time.sleep(10)

if __name__ == "__main__":
    main()