import os.path
import sys
import json
import requests
import ast

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

CLIENT_ACCESS_TOKEN = 'b5273481f5de47c18c8cf184df8e8f86'
LANGUAGE = 'en'  # English


class Bot(object):
    def __init__(self, session_ID):
        global CLIENT_ACCESS_TOKEN
        self.CLIENT_ACCESS_TOKEN = CLIENT_ACCESS_TOKEN
        self.session_ID = session_ID
        self.message = None

    def chat(self, message):
        ai = apiai.ApiAI(self.CLIENT_ACCESS_TOKEN)
        request = ai.text_request()
        request.lang = LANGUAGE
        request.session_id = str(self.session_ID)
        request.query = message
        response = request.getresponse()
        data = json.loads(response.read())
        return data

    def Rate(self, data):
        From = str(data.get('result', {}).get('parameters', {}).get('location', {}).get('city', ''))
        To = str(data.get('result', {}).get('parameters', {}).get('location1', {}).get('city', ''))
        print ("The Customer Enquired about %s to %s") % (From, To)

    def Track(self, data):
        Track = str(data.get('result', {}).get('parameters', {}).get('Tracking_ID', ''))
        # print ("Extracted : " + Track)
        print(Track)
        if Track:
            try:
                Track = ast.literal_eval(Track)
            except:
                pass
        if type(Track) is list and len(Track) > 0:
            Track = Track[0]
        # print ("Extracted Processed: " + Track)
        return Track

    def check_intent_name(self, data):
        intent = str(data.get('result', {}).get('metadata', {}).get('intentName', ''))
        return intent


def track_order(order_id):
    """

    :param order_id:
    :return:
    """
    #TODO": Use PB's trracking APIs

    url = "http://qa.ecourierz.com/api/v1/tracking/"

    payload = json.dumps({"order_ids": str(order_id)})
    # print(payload)
    headers = {
        'content-type': "application/json",
        'x-api-token': "59c6101a94b4af12ecbb2a7e-5d62bb8253d2cb2836ba733b27ff7826491b22bc",

    }

    response = requests.request("POST", url, data=payload, headers=headers)

    # print(response.text)
    return response.json()


if __name__ == '__main__':
    print(track_order('ECZ39794'))
