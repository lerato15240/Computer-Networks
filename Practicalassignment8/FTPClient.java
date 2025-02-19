import java.io.*;
import java.net.*;

public class FTPClient {

    private static final String SERVER_ADDRESS = "localhost";
    private static final int SERVER_PORT = 2121;

    public static void main(String[] args) {
        try (Socket socket = new Socket(SERVER_ADDRESS, SERVER_PORT);
             BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
             PrintWriter out = new PrintWriter(socket.getOutputStream(), true)) {

            String response = in.readLine();
            System.out.println("Server: " + response);

            out.println("USER anonymous");
            response = in.readLine();
            System.out.println("Server: " + response);

            out.println("PASS guest");
            response = in.readLine();
            System.out.println("Server: " + response);

            // Example of downloading a file
            String fileName = "known-good.txt";
            out.println("RETR " + fileName);
            response = in.readLine();
            System.out.println("Server: " + response);

            if (response.startsWith("150")) {
                String filePath = "C:/ftpclient/" + fileName;
                try (PrintWriter fileWriter = new PrintWriter(new FileWriter(filePath))) {
                    while (!(response = in.readLine()).startsWith("226")) {
                        fileWriter.println(response);
                    }
                }
                System.out.println("File " + fileName + " downloaded successfully.");
            }

            out.println("QUIT");
            response = in.readLine();
            System.out.println("Server: " + response);

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
