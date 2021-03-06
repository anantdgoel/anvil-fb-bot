import os
import sys
import json
import uuid, OpenSSL
import requests
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from wit import Wit

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from model import AnvilAppointment #solves circular import problem

db.create_all()
access_token = os.environ['WIT_ACCESS_TOKEN']
contexts = {}
name = None
date = None
email = None
sender_id = None
# appointee = None
appointee = AnvilAppointment(name, email, date)

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

     # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message
                    global sender_id
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    curr_context = {}

                    client.run_actions(sender_id, message_text, curr_context, 25)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))
    qr = list(map(lambda x: {
     "content_type":"text",
      "title": x,
      "payload":"DEVELOPER_DEFINED_PAYLOAD_FOR_PICKING_GREEN"
      } , quick_replies))


    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
             "text": message_text,
            #  "quick_replies":[
            #                      {
            #                       "content_type":"text",
            #                        "title":"Yes",
            #                        "payload":"DEVELOPER_DEFINED_PAYLOAD_FOR_PICKING_GREEN"
            #                        },
            #                       {
            #                         "content_type":"text",
            #                         "title":"No",
            #                         "payload":"DEVELOPER_DEFINED_PAYLOAD_FOR_PICKING_RED"
            #                          }
            #                  ]
         }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()

def first_entity_value(entities, entity):
    """
    Returns first entity value
    """
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val

def add_appointment(request):
    context = request['context']
    entities = request['entities']
    datetime = first_entity_value(entities, 'datetime')
    if datetime:
        # global name
        name = str(get_user_info())
        # global date
        date = str(parse_datetime(datetime))
        appointee.appointment_date = date
        appointee.name = name
        context['date'] = date
        if context.get('missing_date') is not None:
            del context['missing_date']
    else:
        context['missing_date'] = True
        if context.get('date') is not None:
            del context['date']
    return context

def parse_datetime(datetime):
    date_array = datetime[0:datetime.index('T')].split('-')
    date = str(date_array[1]) + '/' + str(date_array[2]) + '/' + str(date_array[0])
    return date

def get_events(request):
    context = request['context']
    page_access_token = os.environ['PAGE_ACCESS_TOKEN']

    result = requests.get('https://graph.facebook.com/v2.8/dummyanvilpage/events?access_token=' + page_access_token).json()

    data = result['data']

    if data:
        message = ''
        for event in data:
            event_name = event['name']
            event_description = event['description']
            event_id = event['id']
            message = message + 'Name: ' + event_name +  '\nDescription:\n' + event_description + '\nLink: ' + 'https://www.facebook.com/events/' + event_id
            message = message + "\n\n"

        message = message[:len(message) - 2]
        context['event'] = message
    else:
        context['event'] = 'Sorry there are no upcoming events!'

    return context

def get_user_info():
    page_access_token = os.environ['PAGE_ACCESS_TOKEN']
    result = requests.get('https://graph.facebook.com/v2.8/' + sender_id + '?fields=first_name,last_name&access_token=' + page_access_token).json()
    first_name = result['first_name']
    last_name = result['last_name']
    name = first_name + ' ' + last_name
    return name

def get_email(request):
    entities = request['entities']
    # global email
    email = first_entity_value(entities, 'email')
    appointee.email = email
    update_db(request)
    return request['context']

def send(request, response):
    send_message(request['session_id'], response['text'])

def update_db(request):
   # print "update_db() vals:\nname: " + str(user_name) + "\nemail: " + str(email) + "\ndate: " + str(appointment_date)
    # global appointee
    # name = str(get_user_info())
    # appointee = AnvilAppointment.query.filter_by(name=name).first()
    # if appointee is None:
    #     appointee = AnvilAppointment(name, email, date)
    #     db.session.add(appointee)
    #     db.session.commit()
    # else:
    #     appointee.name = name
    #     appointee.email = email
    #     appointee.appointment_date = date
    #     db.session.commit()
    db.session.add(appointee)
    db.session.commit()


def delete_apt(request):
    context = request['context']
    name = str(get_user_info())
    appointee = AnvilAppointment.query.filter_by(name=name).first()
    if (appointee is None):
        context['success'] = "We were not able to delete your appointment."
    else:
        db.session.delete(appointee)
        db.session.commit()
        context['success'] = "Your appointment was deleted successfully!"
    return request['context']

def show_apt(request):
    context = request['context']
    name = str(get_user_info())
    appointee = AnvilAppointment.query.filter_by(name=name).first()
    if (appointee is None):
        context['apt_date'] = "You do not currently have an appointment"
    else:
        date = appointee.appointment_date
        context['apt_date'] = "Your current appointment is on " + date

    return context

actions = {
 'send' : send,
  'add_appointment' : add_appointment,
  'show_events' : get_events,
  'get_email' : get_email,
  'delete_apt' : delete_apt,
  'show_apt' : show_apt,
 }

client = Wit(access_token=access_token, actions=actions)

if __name__ == '__main__':
    app.run(debug=True)
