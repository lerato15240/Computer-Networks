import java.io.*;
import java.net.*;

public class FTPServer {

    private static final int PORT = 2121;
    private static final String ROOT_DIRECTORY = "C:/ftpserver/";

    public static void main(String[] args) {
        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            System.out.println("FTP Server started on port " + PORT);

            while (true) {
                Socket clientSocket = serverSocket.accept();
                new ClientHandler(clientSocket).start();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static class ClientHandler extends Thread {
        private Socket clientSocket;
        private PrintWriter out;

        public ClientHandler(Socket clientSocket) {
            this.clientSocket = clientSocket;
        }

        @Override
        public void run() {
            try (BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
                 PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true)) {

                this.out = out;  // Initialize the out variable

                out.println("220 Welcome to Simple FTP Server");

                String command;
                while ((command = in.readLine()) != null) {
                    if (command.startsWith("USER")) {
                        out.println("331 User name okay, need password");
                    } else if (command.startsWith("PASS")) {
                        out.println("230 User logged in, proceed");
                    } else if (command.startsWith("RETR")) {
                        String fileName = command.split(" ")[1];
                        sendFile(fileName);
                    } else if (command.startsWith("STOR")) {
                        String fileName = command.split(" ")[1];
                        receiveFile(fileName, in);
                    } else if (command.equals("QUIT")) {
                        out.println("221 Goodbye");
                        break;
                    } else {
                        out.println("502 Command not implemented");
                    }
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        private void sendFile(String fileName) {
            File file = new File(ROOT_DIRECTORY + fileName);
            if (file.exists() && file.isFile()) {
                out.println("150 File status okay; about to open data connection");
                try (BufferedReader fileReader = new BufferedReader(new FileReader(file))) {
                    String line;
                    while ((line = fileReader.readLine()) != null) {
                        out.println(line);
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
                out.println("226 Closing data connection. Requested file action successful");
            } else {
                out.println("550 File not found");
            }
        }

        private void receiveFile(String fileName, BufferedReader in) {
            File file = new File(ROOT_DIRECTORY + fileName);
            try (PrintWriter fileWriter = new PrintWriter(new FileWriter(file))) {
                out.println("150 File status okay; about to open data connection");
                String line;
                while (!(line = in.readLine()).startsWith("226")) {
                    fileWriter.println(line);
                }
                out.println("226 Closing data connection. Requested file action successful");
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
