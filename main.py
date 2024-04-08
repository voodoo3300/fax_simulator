import email
import imaplib
import os
from email.policy import default
import platform

from conf import accounts
from conf import save_dir
from data_service import DataService
from print_service import print_pdf

data_service = DataService('processed_emails.db')
data_service.connect()

for account in accounts:
    mail = imaplib.IMAP4_SSL(account['server'], account['port'])
    mail.login(account['user'], account['password'])
    mail.select('inbox')

    for search_criteria in account.get('rules', []):
        status, uid_data = mail.uid('search', None, search_criteria)

        for uid in uid_data[0].split():
            if not data_service.email_processed(account['user'], 'inbox', uid.decode()):
                status, data = mail.uid('fetch', uid, '(RFC822)')

                raw_email = data[0][1]
                email_msg = email.message_from_bytes(raw_email, policy=default)

                email_subject = email_msg['subject']
                print(f'E-Mail UID {uid.decode()} - Betreff: {email_subject}')
                data_service.insert_email(
                    account['user'], 'inbox', uid.decode(), 'Processed')

                for part in email_msg.walk():
                    content_disposition = part.get("Content-Disposition")
                    if content_disposition and "attachment" in content_disposition:
                        filename = part.get_filename()
                        if filename.lower().endswith('.pdf'):
                            save_path = os.path.join(save_dir, filename)
                            with open(save_path, 'wb') as f:
                                f.write(part.get_payload(decode=True))
                            if not data_service.db_created:
                                print_pdf(save_path)
    mail.logout()
