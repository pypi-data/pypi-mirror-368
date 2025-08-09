from base64 import b64encode
from datetime import datetime, timezone, timedelta
from multiprocessing.connection import Client
from multiprocessing.connection import Listener
from threading import Thread, Lock
from time import time

import requests
from requests import get


class Premiumy:
    __url = 'https://api.premiumy.net/v1.0/json'

    def __init__(self, api_key: str, port: int = 3010):
        self.__headers = {
            "Content-type": "application/json",
            "Api-Key": api_key
        }

        self.__data = {
            "id": None,
            "jsonrpc": "2.0",
            "method": "sms.mdr_full:get_list",
            "params": {
                "filter": {
                    "start_date": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S'),
                },
            }
        }

        self.report = dict()
        Thread(None, self.__report).start()

        while True:
            with Listener(('localhost', port)) as listener:
                with listener.accept() as conn:
                    conn.send(self.report)

    def __report(self):
        while True:
            # noinspection PyBroadException
            try:
                response = requests.post(url=self.__url, json=self.__data, headers=self.__headers).json()
                self.report.update({row['phone']: row['message'] for row in response['result']['mdr_full_list']})
            except Exception:
                pass


class Sniper:
    __url = "http://51.38.64.110/ints/agent/res/data_smscdr.php"

    def __init__(self, phpsessid, port: int = 3010):
        self.__headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Cookie': f'PHPSESSID={phpsessid}'
        }

        self.report = dict()
        Thread(None, self.__report).start()

        while True:
            with Listener(('localhost', port)) as listener:
                with listener.accept() as conn:
                    conn.send(self.report)

    def __report(self):
        while True:
            # noinspection PyBroadException
            try:
                parameters = {
                    'fdate1': (datetime.now(timezone.utc) - timedelta(minutes=3)).strftime("%Y-%m-%d %H:%M:%S"),
                    'fdate2': (datetime.now(timezone.utc) + timedelta(minutes=3)).strftime("%Y-%m-%d %H:%M:%S"),
                }
                response = requests.post(url=self.__url, params=parameters, headers=self.__headers).json()
                self.report.update({row[2]: row[5] for row in response['aaData'][:-1]})
            except Exception:
                pass


class PSCall:
    __headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-GB,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/131.0.0.0 Safari/537.36',
    }

    def __init__(self, key: str, port: int = 3010):
        # noinspection HttpUrlsUsage
        self.__url = f'http://pscall.net/restapi/smsreport?key={key}'
        self.report = dict()
        Thread(None, self.__report).start()
        while True:
            with Listener(('localhost', port)) as listener:
                with listener.accept() as conn:
                    conn.send(self.report)

    def __report(self):
        while True:
            # noinspection PyBroadException
            try:
                response = get(self.__url, headers=PSCall.__headers, verify=False).json()
                self.report.update({row['num']: row['sms'] for row in response['data']})
            except Exception as _:
                pass


class Ziva:
    def __init__(self, credentials, port: int = 3010):
        self.__page_count = 0
        self.__id = 0
        auth = b64encode(credentials.encode('utf-8')).decode('utf-8')
        self.__headers = {'Authorization': f'Basic {auth}'}
        self.__url = 'http://zivastats.com/rest/sms?per-page=1000'
        self.report = dict()
        Thread(None, self.__report).start()
        while True:
            with Listener(('localhost', port)) as listener:
                with listener.accept() as conn:
                    conn.send(self.report)

    def __report(self):
        while True:
            # noinspection PyBroadException
            try:
                response = get(self.__url, headers=self.__headers, verify=False)
                response = response.json()
                self.report.update({row['destination_addr']: row['short_message'] for row in response})
            except Exception as _:
                pass


class ReportNotRunningError(Exception):
    pass


class ReportReader:
    def __init__(self, port: int = 3010, timeout: int = 30):
        self.port = port
        self.__lock = Lock()
        self.timeout = timeout

    def message(self, number):
        start = time()
        while time() - start < self.timeout:
            try:
                with self.__lock:
                    try:
                        with Client(('localhost', 3010)) as conn:
                            if result := conn.recv().get(number, None):
                                return result
                    except ConnectionRefusedError:
                        raise ReportNotRunningError("Run the report script to receive messages from panels")
            except ConnectionResetError:
                pass
        return None
