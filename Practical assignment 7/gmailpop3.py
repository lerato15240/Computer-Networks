import poplib
import getpass

google_pop3_server = 'pop.gmail.com'

try:
    google_mailbox = poplib.POP3_SSL(google_pop3_server)
    username = input("Enter Gmail username: ")
    password = getpass.getpass("Enter Gmail password: ")
    google_mailbox.user(username)
    google_mailbox.pass_(password)
    num_messages = len(google_mailbox.list()[1])
    print("Inbox: %s" % num_messages)
    for msg in google_mailbox.retr(num_messages)[1]:
        print(msg)
    google_mailbox.quit()
except poplib.error_proto as e:
    print("Authentication failed:", e)
except Exception as e:
    print("An error occurred:", e)
