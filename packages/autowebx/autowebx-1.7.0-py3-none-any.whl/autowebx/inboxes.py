from time import time, sleep

from requests import Session


class Message:
    def __init__(self, uid, sender, subject, received, receiver):
        self.id = uid
        self.sender = sender
        self.subject = subject
        self.received = received
        self.receiver = receiver


class Inboxes:
    def __init__(self, email,  timeout: int = 30):
        url = "https://inboxes.com/api/v2/domain"

        headers = {
            'Host': 'inboxes.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'https://inboxes.com/',
            'DNT': '1',
            'Sec-GPC': '1',
            'Connection': 'close',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Priority': 'u=0'
        }
        self.session = Session()
        self.session.get(url, headers=headers)
        self.timeout = timeout
        self.messages = list()
        self.email = email

    def inbox(self, timeout=None) -> list[Message]:  # 102
        url = f"https://inboxes.com/api/v2/inbox/{self.email}"

        headers = {
            'Host': 'inboxes.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'https://inboxes.com/',
            'authorization': 'Bearer null',
            'DNT': '1',
            'Sec-GPC': '1',
            'Connection': 'close',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Priority': 'u=0'
        }
        start = time()
        while time() - start < (timeout or self.timeout):
            response = self.session.get(url, headers=headers).json()
            if result := [Message(msg['uid'], msg['f'], msg['s'], msg['r'], self.email) for msg in
                          response.get('msgs', [])]:
                for msg in result:
                    self.messages.append(msg)
                    return self.messages
            sleep(0.5)
        return []

    def html(self, msg: Message):  # 2746
        url = f"https://inboxes.com/api/v2/message/{msg.id}"

        headers = {
            'Host': 'inboxes.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'https://inboxes.com/',
            'Content-Type': 'application/json',
            'DNT': '1',
            'Sec-GPC': '1',
            'Connection': 'close',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Priority': 'u=4'
        }

        return self.session.get(url, headers=headers).json()['html']
