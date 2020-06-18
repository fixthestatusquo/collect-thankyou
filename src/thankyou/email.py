from email.message import EmailMessage
from email.headerregistry import Address
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import boto3
import pystache
import requests
import os

class Email:
    @staticmethod
    def address(name, email):
        return Address(display_name=name, addr_spec=email)

    def __init__(_, templateRef, sender=None):
        _.templateRef = templateRef
        _.subject = ''
        _.body = ''
        if sender:
            if isinstance(sender, str):
                _.sender = Address(addr_spec=sender)
            elif isinstance(sender, Address):
                _.sender = sender
        else:
            _.sender = Address(addr_spec=os.environ.get('MAIL_FROM_EMAIL', 'collect@campax.org'),
                               display_name=os.environ.get('MAIL_FROM_NAME', 'Campax'))
        _.attachments = []


    def fetch(_):
        resp = requests.get(_.templateRef)

        if resp.ok:
            camp = resp.json()
            _.body = camp['acf'][ 'thank_you_email_body (PDF - EMAIL)']
            _.subject = camp['acf']['thank_you_email_subject']
        else:
            raise StandardError("Cannot fetch mail template ({})".format(resp.reason))

    def add_attachment(_, filename, blob):
        _.attachments.append({'filename': filename, 'blob': blob})

    
    def build(_, contact):
        msg = EmailMessage()
        msg['Subject'] = pystache.render(_.subject, contact)
        msg['From'] = _.sender
        msg['To'] = Address(display_name=contact['firstName'], addr_spec=contact['email'])

        msg.set_content('Please use an email client to read this message\n')
        msg.add_alternative(pystache.render(_.body, contact), subtype='html')

        for att in _.attachments:
            msg.add_attachment(att['blob'], filename=att['filename'], maintype='application', subtype='pdf')

        return msg

    def send(_, msg):
        ses = boto3.client('ses')
        result = ses.send_raw_email(
            Source=msg['From'],
            Destinations=[msg['To']],
            RawMessage={'Data': msg.as_string()}
        )
        print(result)
        return result
