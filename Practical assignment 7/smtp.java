import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.util.Base64;
import java.util.concurrent.TimeUnit;

import javax.net.ssl.SSLSocket;
import javax.net.ssl.SSLSocketFactory;

public class smtp {
    
    

    public smtp(){
        
    }


   public void sendEmail(String subject, String recipient) throws IOException {

    Socket pingSocket = null;
    PrintWriter out = null;
    BufferedReader in = null;

    try {
        // Connect to SMTP server
        pingSocket = new Socket("smtp.gmail.com", 587);
        out = new PrintWriter(pingSocket.getOutputStream(), true);
        in = new BufferedReader(new InputStreamReader(pingSocket.getInputStream()));

        // Read server response
        String response = in.readLine();
        System.out.println(response);

        // Check if server response indicates successful connection
        if (!response.startsWith("220")) {
            throw new IOException("SMTP server not ready.");
        }

        // Send HELO command
        out.println("HELO smtp.gmail.com");
        System.out.println(in.readLine());

        // Send STARTTLS command to initiate TLS handshake
        out.println("STARTTLS");
        System.out.println(in.readLine());

        // Start TLS session
        SSLSocketFactory factory = (SSLSocketFactory) SSLSocketFactory.getDefault();
        SSLSocket sslSocket = (SSLSocket) factory.createSocket(pingSocket, pingSocket.getInetAddress().getHostAddress(), pingSocket.getPort(), true);
        sslSocket.startHandshake();

        // Update input and output streams to use SSL
        out = new PrintWriter(sslSocket.getOutputStream(), true);
        in = new BufferedReader(new InputStreamReader(sslSocket.getInputStream()));

        // Authenticate with username and password
        String username = recipient; // Replace with your Gmail username
        String password = "buvk noyj ibns clwh"; // Replace with your Gmail password
        out.println("AUTH LOGIN");
        System.out.println(in.readLine());
        out.println(Base64.getEncoder().encodeToString(username.getBytes()));
        System.out.println(in.readLine());
        out.println(Base64.getEncoder().encodeToString(password.getBytes()));
        System.out.println(in.readLine());

        // Send MAIL FROM command
        out.println("MAIL FROM: <" + username + ">");
        System.out.println(in.readLine());

        // Send RCPT TO command
        out.println("RCPT TO: <" + recipient + ">");
        System.out.println(in.readLine());

        // Send DATA command
        out.println("DATA");
        System.out.println(in.readLine());

        // Send email content
        out.println("From: " + username);
        out.println("To: " + recipient);
        out.println("Subject: " + subject);
        out.println();
        out.println("You received this email as a blind carbon copied recipient. Be cautious when replying to all.");
        out.println(".");
        System.out.println(in.readLine());

        // Send QUIT command
        out.println("QUIT");
        System.out.println(in.readLine());

    } catch (IOException e) {
        e.printStackTrace();
    } finally {
        // Close resources
        if (out != null) {
            out.close();
        }
        if (in != null) {
            in.close();
        }
        if (pingSocket != null) {
            pingSocket.close();
        }
    }
}




}