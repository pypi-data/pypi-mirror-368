import time
import requests

DOMAIN = "5sim.net"


class Phone:
    def __init__(self, number_id, phone):
        self.id = number_id
        self.number = phone


class FiveSim:
    def __init__(self, token):
        self.headers = {
            'Authorization': 'Bearer ' + token,
            'Accept': 'application/json',
        }

    def balance(self):
        response = requests.get(f'https://{DOMAIN}/v1/user/profile', headers=self.headers)
        return response.json()['balance']

    def buy_activation_number(self, country: str, operator: str, product: str):
        url = f'https://{DOMAIN}/v1/user/buy/activation/{country}/{operator}/{product}'
        response = requests.get(url, headers=self.headers).json()
        return Phone(response['id'], response['phone'][1:])

    def get_codes(self, phone: Phone, timeout: float = 30):
        start = time.time()
        while True:
            try:
                response = requests.get(f'https://{DOMAIN}/v1/user/check/{phone.id}', headers=self.headers).json()
                return [sms['code'] for sms in response['sms']]
            except (ValueError, IndexError):
                pass

            if time.time() - start > timeout:
                raise TimeoutError


def min_cost_providers(country: str, product: str):
    response = requests.get(f'https://{DOMAIN}/v1/guest/prices?country={country}&product={product}').json()
    operators0 = []
    for operator in response[country][product]:
        if response[country][product][operator]['count'] != 0:
            operators0.append(operator)
    min_cost = response[country][product][operators0[0]]['cost']
    for operator in operators0:
        if response[country][product][operator]['cost'] < min_cost:
            min_cost = response[country][product][operator]['cost']
    operators1 = []
    for operator in operators0:
        if response[country][product][operator]['cost'] == min_cost:
            operators1.append(operator)
    return operators1
