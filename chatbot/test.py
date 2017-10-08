import os.path
import sys
import json

data = "hello"
try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

CLIENT_ACCESS_TOKEN = 'b5273481f5de47c18c8cf184df8e8f86'


def main():
    global data

    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    request = ai.text_request()
    request.lang = 'en'

    request.session_id = "<SESSION ID, UNIQUE FOR EACH USER>"
    human = raw_input("me :")
    request.query = human
    response = request.getresponse()
    data = json.loads(response.read())
    From = str(data.get('result', {}).get('parameters', ''))
    To = str(data.get('result', {}).get('parameters', ''))
    print ("The Coustomer Enquired about %s to %s") % (From, To)


if __name__ == '__main__':
    main()
