import javax.net.ssl.SSLServerSocket;
import javax.net.ssl.SSLSocket;
import javax.net.ssl.SSLSocketFactory;
import java.io.*;
import java.net.Socket;
import java.util.ArrayList;
import java.util.Properties;


import static java.lang.Integer.parseInt;

public class POP3Server {

    public static final int SOCKET_READ_TIMEOUT = 15*1000;
    protected SSLSocket pop3Socket;
    protected BufferedReader in;
    protected PrintWriter out;
    private String host;
    private int port;
    private String userName;
    private String password;


    public POP3Server(String host, String userName, String password,int port) { 

        this.host = host;
        this.userName = userName;
        this.password = password;
        this.port = port;

    }



    protected void checkForError(String response) throws IOException { //Throws exception if given server response if negative. According to POP3
        if (response.charAt(0) != '+')   
            throw new IOException(response);
    }



    public int getMessageCount()  throws IOException {


        String response = doCommand("STAT"); // Send STAT command

        // The format of the response is +OK msg_count size_in_bytes
        // We take the substring from offset 4 (the start of the msg_count) and
        // go up to the first space, then convert that string to a number.

        try {

            String countStr = response.substring(4, response.indexOf(' ', 4));
            int count = parseInt(countStr);
            return count;

        } catch (Exception e) {
            throw new IOException("Negative response:"+ response);

        }

    }


    public String[] getHeaders() throws IOException {

        doCommand("LIST");
        return getMultilineResponse();

    }
    public String getHeader(String messageId) throws IOException {

        String response = doCommand("LIST " + messageId);

        return response;

    }

    public String getMessage(String messageId) throws IOException { // Returns the message using the POP3 command RETR
        doCommand("RETR " + messageId);
        String[] messageLines = getMultilineResponse();
        StringBuffer message = new StringBuffer();
        for (int i=0; i<messageLines.length; i++) {
            message.append(messageLines[i]);
            message.append("\n");
        }

        return new String(message);

    }

    public String[] getMessageHead(String messageId, int lineCount) throws IOException { // Returns the message head using the POP3 command TOP
        doCommand("TOP " + messageId + " " + lineCount);
        return getMultilineResponse();
    }



    public void deleteMessage(String messageId) throws IOException { //Deletes Message using DELE pop3 command
        doCommand("DELE " + messageId);
    }

    public void quit() throws IOException { // Quits the POP3 listener
        doCommand("QUIT");
    }


    public void connectAndAuthenticate() throws IOException {// Make the connection
        SSLSocketFactory factory = (SSLSocketFactory)SSLSocketFactory.getDefault();

        pop3Socket = (SSLSocket) factory.createSocket(host,port);
        pop3Socket.startHandshake();
        pop3Socket.setSoTimeout(SOCKET_READ_TIMEOUT);
        in = new BufferedReader(new InputStreamReader(pop3Socket.getInputStream()));
        out = new PrintWriter(new OutputStreamWriter(pop3Socket.getOutputStream()));

        String response = in.readLine();
        checkForError(response);

        doCommand("USER " + userName);
        doCommand("PASS " + password);

    }





    public void close() {

        try {
            in.close();
            out.close();
            pop3Socket.close();
        } catch (Exception ex) { // Ignore the exception. Probably the socket is not open.
        }

    }


    protected String doCommand(String command) throws IOException { // Sens command to POP3 server

        out.println(command);
        out.flush();
        String response = in.readLine();
        checkForError(response);
        return response;

    }

    protected String[] getMultilineResponse() throws IOException {

        ArrayList lines = new ArrayList();

        while (true) {
            String line = in.readLine();
            if (line == null) {// Server closed connection
                throw new IOException("Server unawares closed the connection.");
            }
            if (line.equals(".")) {// No more lines in the server response
                break;
            }
            if ((line.length() > 0) && (line.charAt(0) == '.')) {// The line starts with a "." - strip it off.
                line = line.substring(1);
            }
            lines.add(line);

        }

        String response[] = new String[lines.size()];
        lines.toArray(response);
        return response;

    }

}