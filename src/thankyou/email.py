from email.message import EmailMessage
from email.headerregistry import Address
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import boto3
import pystache
import requests
import os
import logging


log = logging.getLogger('collect')

class TemplateError(Exception):
    pass

class Email:
    @staticmethod
    def address(name, email):
        return Address(display_name=name, addr_spec=email)

    def __init__(_, templateRef, sender=None):
        _.templateRef = templateRef
        _.subject = ''
        _.body = ''
        _.slug = ''

        if sender:
            if isinstance(sender, str):
                _.sender = Address(addr_spec=sender)
            elif isinstance(sender, Address):
                _.sender = sender
        else:
            _.sender = Address(addr_spec=os.environ.get('FROM_EMAIL', 'collect@campax.org'),
                               display_name=os.environ.get('FROM_NAME', 'Campax'))
        _.attachments = []


    def fetch(_):
        resp = requests.get(_.templateRef)

        if resp.ok:
            camp = resp.json()
            try:
                _.body = camp['acf'][ 'thank_you_email_body']
                _.subject = camp['acf']['thank_you_email_subject']
                _.slug = camp['slug']
            except KeyError as e:
                log.error("no necessary keys in Campaign data:")
                log.error(camp)
                raise e
                
        else:
            raise TemplateError("Cannot fetch mail template ({})".format(resp.reason))

    def add_attachment(_, filename, blob):
        _.attachments.append({'filename': filename, 'blob': blob})

    def has_content(_):
        return len(_.subject) > 0 and len(_.body) > 0
            

    
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
        return result
