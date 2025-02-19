import socket
import random
import threading

# ANSI escape sequences for formatting
ANSI_CLEAR_SCREEN = "\033[2J"
ANSI_MOVE_CURSOR = "\033[{};{}H"

def format_question(question):
    """Format question and answers."""
    formatted_question = question["question"] + "\n"
    for i, answer in enumerate(question["answers"], start=65):
        formatted_question += f"{chr(i)}. {answer[1:]}\n"
    return formatted_question

def select_question(questions):
    """Select a random question."""
    return random.choice(questions)

def check_answer(question, user_answer):
    """Check user's answer."""
    correct_answers = [answer[1:] for answer in question["answers"] if answer.startswith("+")]
    valid_choices = [chr(i) for i in range(65, 65 + len(question["answers"]))]

    if user_answer in valid_choices:
        user_choice_index = ord(user_answer) - 65
        user_choice = question["answers"][user_choice_index][1:]
        if user_choice in correct_answers:
            return True, "Correct! Congratulations!"
        else:
            return False, f"Incorrect. The correct answer(s) is/are: {', '.join(correct_answers)}"
    else:
        return False, "Invalid input. Please enter a valid option (A, B, C, etc.)."


def read_questions(file_path):
    questions = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        question = None
        for line in lines:
            line = line.strip()
            if line.startswith('?'):
                if question:
                    # Add "more than one answer" option if there are multiple correct answers
                    if len([ans for ans in question["answers"] if ans.startswith("+")]) > 1:
                        question["answers"].append("+ More than one answer")
                    # Add "none of the above" option if there are no correct answers
                    elif not any(ans.startswith("+") for ans in question["answers"]):
                        question["answers"].append("+ None of the above")
                    questions.append(question)
                question = {"question": line[1:], "answers": []}
            elif line.startswith('-') or line.startswith('+'):
                question["answers"].append(line)
        if question:
            # Add "more than one answer" option if there are multiple correct answers
            if len([ans for ans in question["answers"] if ans.startswith("+")]) > 1:
                question["answers"].append("+ More than one answer")
            # Add "none of the above" option if there are no correct answers
            elif not any(ans.startswith("+") for ans in question["answers"]):
                question["answers"].append("+ None of the above")
            questions.append(question)
    return questions

def handle_client(conn, questions):
    """Handle client connection."""
    total_score = 0
    continue_answering = True

    while continue_answering:
        question_obj = select_question(questions)
        formatted_question = format_question(question_obj)
        conn.sendall(bytes(ANSI_CLEAR_SCREEN + formatted_question, 'utf-8'))

        correct_answer = [answer[0] for answer in question_obj["answers"] if answer.startswith("+")]
       # conn.sendall(bytes(f"Correct answer(s): {', '.join(correct_answer)}\n", 'utf-8'))

        user_answer = conn.recv(1024).decode('utf-8').strip().upper()
       # conn.sendall(bytes(f"You entered: {user_answer}\n", 'utf-8'))

        response_status, response_msg = check_answer(question_obj, user_answer)
        conn.sendall(bytes(response_msg + "\n", 'utf-8'))

        if response_status:
            total_score += 1

        conn.sendall(bytes("Do you want to continue answering questions? (y/n): ", 'utf-8'))
        continue_response = conn.recv(1024).decode('utf-8').strip().lower()
        if continue_response != "y":
            continue_answering = False
            conn.sendall(bytes(f"Your total score is: {total_score}\n", 'utf-8'))
            conn.close()
            return


def start_server(questions_file):
    """Start the Telnet server."""
    questions = read_questions(questions_file)
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 55555))
    server_socket.listen(5)
    print("Server is listening on port 55555...")

    while True:
        conn, addr = server_socket.accept()
        print(f"Connection established with {addr}")
        
        threading.Thread(target=handle_client, args=(conn, questions)).start()

# Start the server
start_server("questions.txt")
