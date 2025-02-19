import java.io.*;
import java.net.*;
import java.util.*;

public class ClientHandler implements Runnable {
    private Socket clientSocket;
    private List<Map<String, Object>> questions;

    public ClientHandler(Socket clientSocket, List<Map<String, Object>> questions) {
        this.clientSocket = clientSocket;
        this.questions = questions;
    }

    @Override
    public void run() {
        try (
            BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
            PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true)
        ) {
            int totalScore = 0;
            boolean continueAnswering = true;

            while (continueAnswering) {
                Map<String, Object> questionObj = selectQuestion(questions);
                String formattedQuestion = formatQuestion(questionObj);
                out.println(QuizServer.ANSI_CLEAR_SCREEN + formattedQuestion);

                List<String> correctAnswers = new ArrayList<>();
                for (String answer : (List<String>) questionObj.get("answers")) {
                    if (answer.startsWith("+")) {
                        correctAnswers.add(answer.substring(1));
                    }
                }

                String userAnswer = in.readLine().trim().toUpperCase();
                boolean responseStatus;
                String responseMsg;
                if (userAnswer.matches("[A-Z]")) {
                    responseStatus = checkAnswer(questionObj, userAnswer, correctAnswers);
                    responseMsg = responseStatus ? "Correct! Congratulations!" : "Incorrect. The correct answer(s) is/are: " + String.join(", ", correctAnswers);
                } else {
                    responseMsg = "Invalid input. Please enter a valid option (A, B, C, etc.).";
                    responseStatus = false;
                }
                out.println(responseMsg);

                if (responseStatus) {
                    totalScore++;
                }

                out.print("Do you want to continue answering questions? (y/n): ");
                out.flush();
                String continueResponse = in.readLine().trim().toLowerCase();
                if (!continueResponse.equals("y")) {
                    continueAnswering = false;
                    out.println("Your total score is: " + totalScore);
                    out.print("Do you want to email your answers? (y/n): ");
                    out.flush();
                    String emailResponse = in.readLine().trim().toLowerCase();
                    if (emailResponse.equals("y")) {
                        String recipientEmail = getEmail(in, out);
                        String message = "Your Quiz Results:\n" + formattedQuestion + "\nTotal Score: " + totalScore;
                        out.print("email sent! ");
                        sendEmail(recipientEmail, message, totalScore);
                    }
                    clientSocket.close();
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private Map<String, Object> selectQuestion(List<Map<String, Object>> questions) {
        Random random = new Random();
        return questions.get(random.nextInt(questions.size()));
    }

    private String formatQuestion(Map<String, Object> question) {
        StringBuilder formattedQuestion = new StringBuilder((String) question.get("question") + "\n");
        List<String> answers = (List<String>) question.get("answers");
        for (int i = 0; i < answers.size(); i++) {
            formattedQuestion.append((char) (65 + i)).append(". ").append(answers.get(i).substring(1)).append("\n");
        }
        return formattedQuestion.toString();
    }

    private boolean checkAnswer(Map<String, Object> question, String userAnswer, List<String> correctAnswers) {
        List<String> answers = (List<String>) question.get("answers");
        return correctAnswers.contains(answers.get(userAnswer.charAt(0) - 65).substring(1));
    }

    private String getEmail(BufferedReader in, PrintWriter out) throws IOException {
        out.print("Enter your email address: ");
        out.flush();
        return in.readLine().trim();
    }

    private void sendEmail(String recipientEmail, String message, int totalScore) {
        String host = "smtp.freesmtpservers.com";
        int port = 25;
    
        try (Socket socket = new Socket(host, port);
             PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
             BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()))) {
    
            out.println("HELO " + host);
            out.println("MAIL FROM: <testing@cos332.com>");
            out.println("RCPT TO: <" + recipientEmail + ">");
            out.println("DATA");
            out.println("Subject: Your Quiz Results");
            out.println("From: <testing@cos332.com>");
            out.println("To: <" + recipientEmail + ">");
            out.println("");
            out.println("Message-ID: <" + UUID.randomUUID().toString() + "@" + host + ">");
            out.println();
            out.println("MIME-Version: 1.0");
            out.println();
            out.println("Content-Type: text/plain; charset=utf-8");
            out.println();
            out.println("Your Quiz Results:\n" + message + "\nTotal Score: " + totalScore);
            out.println(".");
            out.println("QUIT");
    
            String response;
            while ((response = in.readLine()) != null) {
                System.out.println(response);
            }
    
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    
    


  
    
}
