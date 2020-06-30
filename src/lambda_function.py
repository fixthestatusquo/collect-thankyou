import os
import logging
import json
import boto3
import sentry_sdk
from thankyou import Email
import requests


if 'SENTRY_DSN' in os.environ:
    sentry_sdk.init(os.environ['SENTRY_DSN'])

log = logging.getLogger('collect')
log.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

test_postcard_url = 'https://cloud.cahoots.pl/s/gsn4SsQmcA3nqbQ/download'


def lambda_handler(event, context):
    for rec in event['Records']:
        action = json.loads(rec['body'])
        log.debug('Action id {} with template {}'.format(
            action['actionId'],
            action['actionPage']['thankYouTemplateRef']))

        eml = Email(action['actionPage']['thankYouTemplateRef'])
        eml.fetch()
        if not eml.has_content():
            log.debug('Campaign {} has no email subject or body, not sending email!'.format(eml.slug))
            continue

        postcard = get_postcard(action)
        if postcard:
            postcard_filename ='{}.pdf'.format(eml.slug) 
            eml.add_attachment(postcard_filename, postcard.content)
            log.debug('Attaching postcard with name {}'.format(postcard_filename))
        else:
            log.debug('Cannot retrieve postcard')

        contact = {k: action['contact'][k] for k in ['firstName', 'email', 'ref']}
        contact.update(action['action']['fields'])
        contact['postcardUrl'] = get_postcard_url(action)
        log.debug("Using placeholders: %s", contact)

        if None in contact.values():
            log.error("Missing values in action contact! Action data is: {}".format(action))
            return {'status': 'error'}

        msg = eml.build(contact)
        try:
            sent = eml.send(msg)
            log.debug('Sent %s', sent.get('MessageId','?'))
        except ClientError as e:
            log.error('actionId=%d: %s', action['actionId'], e.response['Error']['Message'])

    return {'status': 'ok'}

def get_postcard_url(action):
    postcard_url = action['action']['fields'].get('postcardUrl') or test_postcard_url
    postcard_url += '&qrcode={}:{}'.format(action['contact']['ref'], action['actionPageId'])
    return postcard_url


def get_postcard(action):
    postcard_url = get_postcard_url(action)
    log.debug("postcardUrl = {}".format(postcard_url))

    postcard = requests.get(postcard_url)
    if postcard.ok:
        return postcard
    else:
        return None


def attribute(rec, an):
    return rec['messageAttributes'][an]['stringValue']
