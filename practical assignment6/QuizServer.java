import java.io.*;
import java.net.*;
import java.util.*;

public class QuizServer {
    // ANSI escape sequences for formatting
    public static final String ANSI_CLEAR_SCREEN = "\033[2J";
    public static final String ANSI_MOVE_CURSOR = "\033[%d;%dH";

    public static void main(String[] args) {
        startServer("questions.txt");
    }

    public static void startServer(String questionsFile) {
        List<Map<String, Object>> questions = readQuestions(questionsFile);
        ServerSocket serverSocket = null;

        try {
            serverSocket = new ServerSocket(55555);
            System.out.println("Server is listening on port 55555...");

            while (true) {
                Socket clientSocket = serverSocket.accept();
                System.out.println("Connection established with " + clientSocket.getRemoteSocketAddress());
                new Thread(new ClientHandler(clientSocket, questions)).start();
            }
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if (serverSocket != null) {
                try {
                    serverSocket.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    public static List<Map<String, Object>> readQuestions(String filePath) {
        List<Map<String, Object>> questions = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String line;
            Map<String, Object> question = null;
            while ((line = br.readLine()) != null) {
                line = line.trim();
                if (line.startsWith("?")) {
                    if (question != null) {
                        questions.add(question);
                    }
                    question = new HashMap<>();
                    question.put("question", line.substring(1));
                    question.put("answers", new ArrayList<String>());
                } else if (line.startsWith("-") || line.startsWith("+")) {
                    ((List<String>) question.get("answers")).add(line);
                }
            }
            if (question != null) {
                questions.add(question);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return questions;
    }
}
