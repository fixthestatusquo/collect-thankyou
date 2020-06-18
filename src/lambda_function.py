import os
import logging
import jsonpickle
import boto3
import sentry_sdk


if 'SENTRY_DSN' in os.environ:
    sentry_sdk.init(os.environ['SENTRY_DSN'])

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    queue = get_queues()

    for rec in event['Records']:
        action_type = attribute(rec, 'ActionType')
        logger.info("Action type is {} (DOWNLOAD_ACTION_TYPE={})".format(action_type, os.environ.get('DOWNLOAD_ACTION_TYPE', 'download')))
        if action_type == os.environ.get('DOWNLOAD_ACTION_TYPE', 'download'):
            sqs.send_message(QueueUrl=queue['thankyou'], DelaySeconds=30, MessageBody=rec['body'])

        sqs.send_message(QueueUrl=queue['identity'], MessageBody=rec['body'])

    return {'status': 'ok'}


def attribute(rec, an):
    return rec['messageAttributes'][an]['stringValue']

def get_queues():
    try:
        tyq = os.environ.get('THANKYOU_QUEUE', 'action_thankyou')
        idq = os.environ.get('IDENTITY_QUEUE', 'action_identity')
        logger.info("Getting thank you queue {}".format(tyq))
        logger.info("Getting identity queue {}".format(idq))
        return {
            'thankyou': sqs.get_queue_url(QueueName=tyq)['QueueUrl'],
            'identity': sqs.get_queue_url(QueueName=idq)['QueueUrl']
        }
    except sqs.exceptions.QueueDoesNotExist as e:
        logger.error("Cannot get queue. thank you queue: {}, identity queue: {}".format(tyq, idq))
        raise e



# Campax widget:
# https://widget.proca.foundation/d/campax.en/index.html

