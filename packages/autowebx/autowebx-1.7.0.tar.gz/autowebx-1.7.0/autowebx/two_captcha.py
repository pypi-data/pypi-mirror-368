from random import randint
from time import time, sleep

from requests import post


class CaptchaError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class CaptchaType:
    recaptchaV3 = 'RecaptchaV3TaskProxyless'
    recaptchaV2 = 'RecaptchaV2TaskProxyless'


class TwoCaptcha:
    def __init__(
            self,
            apikey: str,
            captcha_type: str,
            website_url: str,
            website_key: str,
            is_invisible: bool = False,
            user_agent: str = None,
            cookies: str = None,
    ):
        self.client_key = apikey

        data = {
            "clientKey": apikey,
            "task": {
                "type": captcha_type,
                "websiteURL": website_url,
                "websiteKey": website_key,
                "isInvisible": is_invisible,
                "userAgent": user_agent,
                "cookies": cookies,
            }
        }

        response = post('https://api.2captcha.com/createTask', json=data).json()
        self.task_id = response.get('taskId', None)
        if self.task_id is None:
            raise CaptchaError(
                f'{response["errorCode"]}: {response["errorDescription"]} (error id: {response['errorId']})'
            )
        self.submit_time = time()

    def solution(self, timeout=100):
        while time() < self.submit_time + randint(15, 20):
            pass

        data = {
            "clientKey": self.client_key,
            "taskId": self.task_id
        }
        start = time()
        while time() < start + timeout:
            try: response = post('https://api.2captcha.com/getTaskResult', json=data).json()
            except ConnectionError: continue

            if response.get('status', None) == 'processing':
                print('.', end='')
                sleep(5)
            elif (error_id := response['errorId']) != 0:
                raise CaptchaError(f'{response["errorCode"]}: {response["errorDescription"]} (error id: {error_id})')

            else: return response['solution']['gRecaptchaResponse']
        raise CaptchaError(f'CaptchaTimeout: {timeout}s exceeded')


class NormalCaptcha:
    def __init__(self, apikey: str, image: str):
        self.client_key = apikey
        data = {
            "clientKey": apikey,
            "task": {
                "type": "ImageToTextTask",
                "body": image,
                "case": True,
            }
        }
        response = post('https://api.2captcha.com/createTask', json=data).json()
        self.task_id = response.get('taskId', None)
        if self.task_id is None:
            raise CaptchaError(
                f'{response["errorCode"]}: {response["errorDescription"]} (error id: {response['errorId']})'
            )

    def solution(self, timeout=30):
        data = {
            "clientKey": self.client_key,
            "taskId": self.task_id
        }

        start = time()
        while time() < start + timeout:
            try: response = post('https://api.2captcha.com/getTaskResult', json=data).json()
            except ConnectionError: continue

            if response.get('status', None) == 'processing':
                sleep(1)

            elif (error_id := response['errorId']) != 0:
                raise CaptchaError(f'{response["errorCode"]}: {response["errorDescription"]} (error id: {error_id})')

            else: return response['solution']['text']
        raise CaptchaError(f'CaptchaTimeout: {timeout}s exceeded')


class Turnstile:
    def __init__(self, apikey, website_url, site_key):
        self.apikey = apikey

        data = {
            "clientKey": apikey,
            "task": {
                "type": "TurnstileTaskProxyless",
                "websiteURL": website_url,
                "websiteKey": site_key,
            }
        }

        response = post('https://api.2captcha.com/createTask', json=data).json()
        self.task_id = response.get('taskId', None)
        if self.task_id is None:
            raise CaptchaError(
                f'{response["errorCode"]}: {response["errorDescription"]} (error id: {response['errorId']})'
            )

    def solution(self, timeout: float = 30.0):
        data = {
            "clientKey": self.apikey,
            "taskId": self.task_id
        }
        start = time()
        while time() < start + timeout:
            try: response = post('https://api.2captcha.com/getTaskResult', json=data).json()
            except ConnectionError: continue

            if response.get('status', None) == 'processing':
                sleep(1)

            elif (error_id := response['errorId']) != 0:
                raise CaptchaError(f'{response["errorCode"]}: {response["errorDescription"]} (error id: {error_id})')

            else: return response['solution']['token']
        raise CaptchaError(f'CaptchaTimeout: {timeout}s exceeded')



if __name__ == '__main__':
    Turnstile('eaa8df1420ded6e5d3004d9bf3b15375', 'https://www.loman.ai/', '0x4AAAAAAAQTptj2So4dx43e').solution()