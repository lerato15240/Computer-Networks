import java.io.*;
import java.nio.file.*;
import java.security.*;

public class FileMonitor {

    private static final String MONITORED_FILE_PATH = "C:/ftpclient/protected_file.txt";
    private static final String KNOWN_GOOD_FILE_PATH = "known-good.txt";
    private static final String FTP_SERVER = "localhost";
    private static final int FTP_PORT = 2121;  
    public static void main(String[] args) {
        try {

            File protectedFile = new File(MONITORED_FILE_PATH);
            if (!protectedFile.exists()) {
                createInitialProtectedFile();
            }

            String originalHash = computeFileHash(MONITORED_FILE_PATH);

            while (true) {
                if (!Files.exists(Paths.get(MONITORED_FILE_PATH)) || !originalHash.equals(computeFileHash(MONITORED_FILE_PATH))) {
                    System.out.println("File modified or missing. Restoring...");
                    FTPClient.main(new String[]{});
                    originalHash = computeFileHash(MONITORED_FILE_PATH);
                }
                Thread.sleep(60000); 
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static String computeFileHash(String filePath) throws IOException, NoSuchAlgorithmException {
        MessageDigest digest = MessageDigest.getInstance("MD5");
        try (InputStream is = Files.newInputStream(Paths.get(filePath));
             DigestInputStream dis = new DigestInputStream(is, digest)) {
            byte[] buffer = new byte[4096];
            while (dis.read(buffer) != -1) {
               
            }
        }
        byte[] hashBytes = digest.digest();
        StringBuilder sb = new StringBuilder();
        for (byte b : hashBytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }

    private static void createInitialProtectedFile() throws IOException {
        String initialContent = "Good";
        Files.write(Paths.get(MONITORED_FILE_PATH), initialContent.getBytes());
        System.out.println("Created initial protected file with content: " + initialContent);
    }
}
