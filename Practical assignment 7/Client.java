import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Scanner;
import java.util.StringTokenizer;

public class Client {

    static final String POP3_HOST = "pop.gmail.com";
    static final String POP3_USERNAME = "lerato15278@gmail.com";
    static final String POP3_PASSWORD = "buvk noyj ibns clwh";
    static final int POP3_PORT = 995;

    public static String getSender(String[] array){

        String temp = null;
        String sender = null;
        int indexS =0;
        int indexE =0;

        for (int i = 0 ; i < array.length;i++){
            if(array[i].startsWith("From")){
                temp = array[i];
                for (int j = 0 ; j < temp.length();j++){
                    if(temp.charAt(j) == '<'){
                        indexS = j+1;
                    }
                    if(temp.charAt(j)=='>'){
                        indexE = j;
                    }

                }
                if( indexS==0 && indexE==0 ){
                    sender = temp.substring(6,temp.length());  
                } 
                else{
                    sender = temp.substring(indexS,indexE);
                }
                
            }




        }
        return sender;
    }

    public static String getSubject(String[] array){
        String temp = null;
        String subject="no subject";
        for (int i = 0 ; i < array.length;i++){
            if(array[i].startsWith("Subject")){
                temp = array[i];
                subject = temp.substring(9);

            }
        }
        return subject;
    }
    public static void main(String[] args) throws InterruptedException {
        Thread thread = new Thread();

        while(true){
            POP3Server POP3client = new POP3Server(POP3_HOST,POP3_USERNAME,POP3_PASSWORD,POP3_PORT);
            smtp smtpSender = new smtp();

            try  {

                System.out.println("Connecting to POP3 server...");
                POP3client.connectAndAuthenticate();
                System.out.println("Connected to POP3 server.");
                int messageCount = POP3client.getMessageCount();
                System.out.println("\nNumber of messages  : " + messageCount);
                String[] messages = POP3client.getHeaders();

                for (int i=0; i<messages.length; i++) {

                    StringTokenizer messageTokens = new StringTokenizer(messages[i]);
                    String messageId = messageTokens.nextToken();
                    String[] messageBody = POP3client.getMessageHead(messageId,1);
                    System.out.println("Message  : "+messageId);

                    System.out.println(getSender(messageBody));
                    for (int j = 0; j < messageBody.length; j++) {
                        System.out.println(messageBody[j]);
                    }
                    

                    boolean containsCc = false;
                    

                    for (String line : messageBody) {
                        if (line.contains("Bcc: Lerato15278@gmail.com")) {
                            containsCc = true;
                        }
                        
                    }

                    if (containsCc ) {
                        //send email using smpt here
                        System.out.println("sending email");
                        String subject = "Subject: BCC EMAIL recieved" + getSubject(messageBody);
                        smtpSender.sendEmail(subject,POP3_USERNAME);
                        System.out.println("Email sent");
                        
                    }



                    

                }
            } catch (Exception e) {
                POP3client.close();
                System.out.println("Error Receiving Messages");
                e.printStackTrace();
                
            }

            thread.sleep(10000);
        }



    }

}