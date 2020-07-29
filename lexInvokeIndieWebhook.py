"""
This sample demonstrates an implementation of the Lex Code Hook Interface
in order to serve a sample bot which manages reservations for hotel rooms and car rentals.
Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
as part of the 'BookTrip' template.

For instructions on how to set up and test this bot, as well as additional samples,
visit the Lex Getting Started documentation http://docs.aws.amazon.com/lex/latest/dg/getting-started.html.
"""

import json
import datetime
import time
import os
import dateutil.parser
import logging
import boto3
from botocore.vendored import requests

client = boto3.client('lex-models')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# --- Helpers that build all of the responses ---


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def confirm_intent(session_attributes, intent_name, slots, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }

def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None

def callFulFillmentService(intent_name, intent_slots):
    
    response = client.get_intent(
        name=intent_name,
        version='$LATEST'
    )
    
    message = response['conclusionStatement']['messages'][0]['content']
    logger.debug(message)
    
    headers = {'Content-Type': 'application/json'}
    
    api_url = 'https://e127b6288544.ngrok.io/indie/webhook'
    
    payload = {'intent_id': intent_name, 
        'slot_values': intent_slots, 
        'response_template': message}
    
    logger.debug(payload)

    response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code == 200:
        logger.debug(json.loads(response.content.decode('utf-8')))
    else:
        logger.debug(response.status_code)
    
    return close(
        None,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': json.loads(response.content.decode('utf-8'))['fulfillment_message']
        }
    )

def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """
    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))
    
    
    slots = {}
    try:
        slots = intent_request['currentIntent']['slots']
    except KeyError:
        logger.debug("Slots are empty")
    
    if intent_request['invocationSource'] == 'FulfillmentCodeHook':
        return callFulFillmentService(intent_request['currentIntent']['name'], slots)
        
    raise Exception('Invocation Source ' + intent_request['invocationSource'] + ' not supported')

def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)