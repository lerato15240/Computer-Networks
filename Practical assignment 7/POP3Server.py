import imaplib
import email
from email.header import decode_header

# IMAP settings
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993
EMAIL = 'lerato15278@gmail.com'
PASSWORD = 'buvk noyj ibns clwh'

def decode_email_header(header):
    # Decode email header
    decoded_parts = decode_header(header)
    decoded_header = ''
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            if encoding:
                decoded_header += part.decode(encoding)
            else:
                decoded_header += part.decode()
        else:
            decoded_header += part
    return decoded_header

def fetch_emails():
    # Connect to the IMAP server
    imap = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)

    # Login to the email account
    imap.login(EMAIL, PASSWORD)

    # Select the mailbox (inbox)
    imap.select('inbox')

    # Search for all emails
    _, data = imap.search(None, 'ALL')

    # Iterate through the list of email IDs
    for num in data[0].split():
        # Fetch the email using its ID
        _, raw_email = imap.fetch(num, '(RFC822)')
        email_message = email.message_from_bytes(raw_email[0][1])

        # Extract email details
        sender = decode_email_header(email_message['From'])
        subject = decode_email_header(email_message['Subject'])

        # Print email details
        print(f"From: {sender}")
        print(f"Subject: {subject}")

    # Logout from the email account
    imap.logout()

if __name__ == "__main__":
    fetch_emails()
