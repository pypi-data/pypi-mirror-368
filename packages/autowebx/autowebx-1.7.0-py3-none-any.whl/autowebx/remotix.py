import json
import os
import random
from socket import gethostname
from threading import Thread
from time import sleep
from typing import Optional, Any

from requests import post

from autowebx.auto_save_dict import AutoSaveDict

BASE_URL = 'https://www.remotix.app'


class InvalidKey(Exception):
    pass

class Run:
    def __init__(self, key: str, stats: Optional[dict[str, Any]] = None,  *files: str):
        base_dir = os.path.join(os.getenv("APPDATA"), 'Remotix')
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        file_path = os.path.join(base_dir, "data.json")
        asd = AutoSaveDict(file_path)
        device_name = gethostname()
        if devic_id := asd.get('device_id', None, False):
            url = f'{BASE_URL}/api/verify/?api_key={key}&device_id={devic_id}&device_name={device_name}'
            if not (response := post(url).json())['valid']:
                raise InvalidKey(response['message'])
            asd['device_id'] = response['device_id']

        else:
            url = f'{BASE_URL}/api/verify/?api_key={key}&device_name={device_name}'
            asd['device_id'] = (response := post(url).json())['device_id']
            if not response['valid']:
                raise InvalidKey(response['message'])

        url = f'{BASE_URL}/usage/'
        data = {
            'api_key': key,
            'device_id': asd['device_id'],
            'stats': json.dumps(stats),
        }
        response = post(
            url,
            data=data,
            files=[("files", (file.split('/')[-1], open(file, "rb"), "text/plain")) for file in
                   files] if files else None
        )

        self.__run_id = response.json()['run_id']

        self.__key = key
        self.__stats = dict()
        self.__done = False

        Thread(None, self.__log, 'log').start()

    def __log(self):
        while not self.__done:
            # noinspection PyBroadException
            try:
                url = f'{BASE_URL}/usage/'
                data = {
                    'api_key': self.__key,
                    'run_id': self.__run_id,
                    'stats': json.dumps(self.__stats)
                }
                post(url, data=data)
            except Exception:
                pass

    def log(self, key: str) -> None:
        self.__stats[key] = self.__stats.get(key, 0) + 1

    def done(self):
        self.__done = True


if __name__ == '__main__':
    run = Run(
        'bcab38ce-cd3a-4948-83f0-f577513a21e7',
        {'threads': 3, 'total': 10}
    )

    for _ in range(1000):
        run.log(random.choices(['Success', 'Fail'], weights=[90, 10], k=1)[0])
        sleep(random.uniform(0, 1))

    run.done()

