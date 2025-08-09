from typing import Optional

from bs4 import BeautifulSoup
from requests import post

BASE_URL = 'https://22.do/api/v2'


class PurchaseError(Exception):
    pass


class EmailGenerationError(Exception):
    pass


class InboxRetrievalError(Exception):
    pass


class TwentyTwoDo:
    def __init__(self, api_token):
        response = post(BASE_URL + '/token', json={'token': api_token}).json()
        if response['code'] == 200:
            self.__headers = {'Authorization': f'Bearer {response['data']['Bearer']}'}
        else:
            raise PermissionError(response['msg'])

    class Message:
        def __init__(self, message_id: str, headers: dict):
            response = post(BASE_URL + '/inbox/message', json={'messageId': message_id}, headers=headers).json()
            if response['code'] == 200:
                self.subject = response['data']['subject']
                self.body = response['data']['body']
                self.html = BeautifulSoup(response['data']['html'], 'html.parser')
                self.sender = response['data']['from']


    def purchase_gmail(self, number: int = 1):
        response = post(BASE_URL + '/gmail/purchase', json={'number': number}, headers=self.__headers).json()
        if response['code'] != 200:
            raise PurchaseError(response['msg'])

    def generate_gmail(self):
        response = post(BASE_URL + '/gmail/generate', json={'number': 1, 'plus': False}, headers=self.__headers).json()
        if response['code'] == 200:
            return f'{response['data']['items'][0]}@gmail.com'
        else:
            raise EmailGenerationError(response['msg'])

    def inbox(self, email: str, time: Optional[int] = None):
        response = post(BASE_URL + '/gmail/inbox', json={'email': email, 'time': time}, headers=self.__headers).json()
        if response['code'] == 200:
            return [self.Message(message['messageId'], self.__headers) for message in response['data']]
        else:
            raise InboxRetrievalError(response['msg'])


if __name__ == '__main__':
    TwentyTwoDo('179942273717c7d40ce8be256c7a1b62').inbox('eopss.jks.h.yie.haias.h.ko@gmail.com')
