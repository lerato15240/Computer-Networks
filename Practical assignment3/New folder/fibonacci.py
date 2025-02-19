import socket
import re

# Function to read three numbers from a text file and calculate the next Fibonacci number
def calculate_next_fibonacci():
    with open('fibonacci.txt', 'r') as file:
        numbers = list(map(int, file.readline().split(',')))
    next_number = sum(numbers[-2:])
    numbers.append(next_number)
    with open('fibonacci.txt', 'w') as file:
        file.write(','.join(map(str, numbers[-3:])))
    return numbers[-3:]

# Function to calculate the previous Fibonacci numbers
def calculate_previous_fibonacci():
    with open('fibonacci.txt', 'r') as file:
        numbers = list(map(int, file.readline().split(',')))
    previous_numbers = [numbers[1] - numbers[0], numbers[0], numbers[1]]
    with open('fibonacci.txt', 'w') as file:
        file.write(','.join(map(str, previous_numbers)))
    return previous_numbers

# Function to generate HTML response with the next Fibonacci numbers
def generate_html(numbers):
    html = "<html><body>"
    html += "<h1>Next Fibonacci Numbers:</h1>"
    html += "<p>{}, {}, {}</p>".format(*numbers)
    html += "<form action='/' method='get'>"
    if numbers != [0, 1, 1]:  # Check if current numbers are not 0, 1, 1
        html += "<input type='submit' name='prev' value='Previous'>"
    html += "<input type='submit' name='next' value='Next'>"
    html += "</form>"
    html += "</body></html>"
    return html

# Function to handle client requests
def handle_client(client_socket):
    request_data = client_socket.recv(1024).decode()
    match = re.match(r"GET\s+(/[^?\s]*)", request_data)
    if match:
        path = match.group(1)
        if path == "/" or path == "/fibonacci":
            if "next" in request_data:
                next_numbers = calculate_next_fibonacci()
            else:
                next_numbers = calculate_previous_fibonacci()
            html = generate_html(next_numbers)
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {}\r\n\r\n{}".format(len(html), html)
        else:
            response = "HTTP/1.1 404 Not Found\r\nContent-Length: 9\r\n\r\nNot Found"
    else:
        response = "HTTP/1.1 400 Bad Request\r\nContent-Length: 11\r\n\r\nBad Request"
    client_socket.send(response.encode())
    client_socket.close()

# Function to start the server
def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print("Server listening on {}:{}".format(host, port))
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print("Accepted connection from {}:{}".format(client_address[0], client_address[1]))
            handle_client(client_socket)
    except KeyboardInterrupt:
        print("Server shutting down...")
        server_socket.close()

if __name__ == "__main__":
    HOST = '127.0.0.1'  # Localhost
    PORT = 55555
    start_server(HOST, PORT)
