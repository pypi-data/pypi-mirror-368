from random import randint
from time import time, sleep

from requests import post


class RecaptchaV2:
    def __init__(self, apikey: str, website_url: str, website_key: str, is_invisible: bool = False):
        self.client_key = apikey

        data = {
            "clientKey": apikey,
            "task": {
                "type": "RecaptchaV2TaskProxyless",
                "websiteURL": website_url,
                "websiteKey": website_key,
                "isInvisible": is_invisible
            }
        }

        response = post('https://api.capsolver.com/createTask', json=data).json()
        self.task_id = response['taskId']
        self.submit_time = time()

    def solution(self, timeout=randint(15, 20)):
        while time() < self.submit_time + timeout:
            pass

        data = {
            "clientKey": self.client_key,
            "taskId": self.task_id
        }

        while True:
            response = post('https://api.capsolver.com/getTaskResult', json=data).json()
            if response['status'] == 'processing':
                sleep(5)
            elif error_id := response['errorId'] != 0:
                raise Exception(f'{error_id}:{response["errorCode"]}:{response["errorDescription"]}')
            else:
                return response['solution']['gRecaptchaResponse']
