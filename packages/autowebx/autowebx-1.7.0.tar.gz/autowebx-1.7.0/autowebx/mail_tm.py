import random

from requests import get, post

from autowebx.account import Account

_BASE_URL = 'https://api.mail.tm'
_DOMAINS = None

def domains():
    global _DOMAINS
    if _DOMAINS:
        return _DOMAINS

    response = get(_BASE_URL + '/domains').json()
    _DOMAINS = [member.get('domain') for member in response.get('hydra:member')]
    return _DOMAINS


class Message:
    def __init__(self, message_id: str, text: str, html: list[str]):
        self.id = message_id
        self.text = text
        self.html = html


class MailTmAccount(Account):
    def __init__(self, **kwargs):
        if not kwargs.get('domain'):
            kwargs['domain'] = random.choice(domains())

        super().__init__(**kwargs)
        post(f'{_BASE_URL}/accounts', json={'address': self.email, 'password': self.password})
        response = post(_BASE_URL + '/token', json={'address': self.email, 'password': self.password}).json()
        self.token = response['token']

    def messages(self):
        response = get(_BASE_URL + '/messages', headers={'Authorization': f'Bearer {self.token}'}).json()
        return [self._message(message['id']) for message in response['hydra:member']]

    def _message(self, message_id: str):
        response = get(f'{_BASE_URL}/messages/{message_id}', headers={'Authorization': f'Bearer {self.token}'}).json()
        return Message(message_id, response['text'], response['html'])
