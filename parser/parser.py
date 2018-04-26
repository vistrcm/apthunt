import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def handler(event, context):
    """request handler"""
    logger.debug(event)

    return respond(None, event)
