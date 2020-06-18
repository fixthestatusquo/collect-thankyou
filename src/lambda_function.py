import os
import logging
import json
import boto3
import sentry_sdk
from thankyou import Email
import requests


if 'SENTRY_DSN' in os.environ:
    sentry_sdk.init(os.environ['SENTRY_DSN'])

logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO'))

test_postcard_url = 'https://cloud.cahoots.pl/s/gsn4SsQmcA3nqbQ/download'


def lambda_handler(event, context):
    for rec in event['Records']:
        action = json.loads(rec['body'])
        logging.debug('Action id {} with template {}'.format(
            action['actionId'],
            action['actionPage']['thankYouTemplateRef']))


        eml = Email(action['actionPage']['thankYouTemplateRef'])
        eml.fetch()
        if not eml.has_content():
            logging.debug('Campaign {} has no email subject or body, not sending email!'.format(eml.slug))
            continue

        postcard = get_postcard(action)
        if postcard:
            postcard_filename ='{}.pdf'.format(eml.slug) 
            eml.add_attachment(postcard_filename, postcard.content)
            logging.debug('Attaching postcard with name {}'.format(postcard_filename))
        else:
            logging.debug('Cannot retrieve postcard')

        contact = {k: action['contact'][k] for k in ['firstName', 'email', 'ref']}
        contact.update(action['action']['fields'])
        logging.debug("Using placeholders: %s", contact)
        msg = eml.build(contact)
        try:
            sent = eml.send(msg)
            logging.debug('Sent %s', sent.get('MessageId','?'))
        except ClientError as e:
            logging.error('actionId=%d: %s', action['actionId'], e.response['Error']['Message'])

    return {'status': 'ok'}


def get_postcard(action):
    postcard_url = action['action']['fields'].get('postcardUrl') or test_postcard_url
    postcard = requests.get(postcard_url)
    if postcard.ok:
        return postcard
    else:
        return None


def attribute(rec, an):
    return rec['messageAttributes'][an]['stringValue']
