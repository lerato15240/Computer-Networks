import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class TransactionProcessor {

    public static void main(String[] args) {
        String inputFileName = "file2.txt";
        String outputFileName = "output.txt";

        // A map to keep track of each person's total
        Map<String, Double> totals = new HashMap<>();
        double totalTenPercentOverFifty = 0.0;

        try (BufferedReader br = new BufferedReader(new FileReader(inputFileName))) {
            String line;

            while ((line = br.readLine()) != null) {
                // Split the line by spaces
                String[] parts = line.split(" ");

                // Extract surname and initials
                String surname = parts[0];
                String initials = parts[1];

                // Generate a unique key for the person
                String personKey = surname + " " + initials;

                // Extract the last amount (the last numeric part in the line)
                String lastAmountStr = parts[parts.length - 1].replace(",", ".");
                double lastAmount = Double.parseDouble(lastAmountStr);

                // Sum the total for each person
                totals.put(personKey, totals.getOrDefault(personKey, 0.0) + lastAmount);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

        try (BufferedWriter bw = new BufferedWriter(new FileWriter(outputFileName))) {
            for (Map.Entry<String, Double> entry : totals.entrySet()) {
                String person = entry.getKey();
                double totalAmount = entry.getValue();

                // Calculate 10% and 40% of the total amount
                double tenPercent = totalAmount * 0.10;
                double fortyPercent = totalAmount * 0.40;
                // Calculated 10% overfifty total
                if (tenPercent > 50) {
                    totalTenPercentOverFifty += tenPercent;
                }

                int personWidth = 20;
                int percentWidth = 10;
                int totalAmountWidth = 10;

                // Write the output line
                String outputLine = String.format("%-" + personWidth + "s %"
                        + percentWidth + ".2f(%"
                        + ".2f) %"
                        + totalAmountWidth + ".2f",
                        person, fortyPercent, tenPercent, totalAmount);
                bw.write(outputLine);
                bw.newLine();
            }
            
            bw.newLine();
            bw.write(String.format("%-20s %10s(%.2f) %10s", "Total 10% over R50", "", totalTenPercentOverFifty, ""));
            bw.newLine();

            System.out.println("Processing complete. Output written to " + outputFileName);

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
