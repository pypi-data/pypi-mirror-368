import random

from multipledispatch import dispatch
from requests import get, post

from autowebx.account import generate_username

domains = [domain['name'] for domain in get("https://api.internal.temp-mail.io/api/v4/domains").json()['domains']]


class Email:
    @dispatch(str, str)
    def __init__(self, name: str = generate_username(), domain: str = random.choice(domains)):
        payload = {"name": name, "domain": domain}
        response = post('https://api.internal.temp-mail.io/api/v3/email/new', json=payload).json()
        self.address = response['email']
        self.token = response['token']

    @dispatch(int, int)
    def __init__(self, min_name_length: int = 10, max_name_length: int = 10):
        payload = {"min_name_length": min_name_length, "max_name_length": max_name_length}
        response = post('https://api.internal.temp-mail.io/api/v3/email/new', json=payload).json()
        self.address = response['email']
        self.token = response['token']

    @dispatch()
    def __init__(self):
        self.__init__(10, 10)

    def get_messages(self):
        return get_messages(self.address)


def get_messages(email: str):
    response = get(f'https://api.internal.temp-mail.io/api/v3/email/{email}/messages').json()
    messages = [Message(message['id'], message['body_text'], message['body_html']) for message in response]
    return messages[0] if len(messages) == 1 else messages


class Message:
    def __init__(self, id_: str, body_text: str, body_html: str):
        self.id = id_
        self.body_text = body_text
        self.body_html = body_html

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return other is Message and self.id == other.id
