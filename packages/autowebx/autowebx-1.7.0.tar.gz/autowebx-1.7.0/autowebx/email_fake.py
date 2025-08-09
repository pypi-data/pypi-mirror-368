import re
from time import time

from bs4 import BeautifulSoup, Tag, ResultSet
from bs4.element import PageElement, NavigableString
from requests import get, post, ConnectTimeout, ConnectionError


def get_suggestions():
    html = get("https://email-fake.com/").text
    soup = BeautifulSoup(html, "html.parser")
    return [child.text for child in soup.find('div', class_="tt-suggestions").children]


def get_message(
        email: str | Tag, timeout: int | float = 30
) -> None | PageElement | BeautifulSoup | NavigableString | ResultSet[Tag]:
    if isinstance(email, str):
        url = "https://email-fake.com/"
        username, domain = email.split("@")
        surl = f'{domain}/{username}'
        start = time()
        exception = None
        while time() - start < timeout:
            try:
                response = get(url, cookies={'surl': surl}).text
                soup = BeautifulSoup(response, 'html.parser')
                tag = soup.find('div', class_='mess_bodiyy')
                if tag:
                    delll = re.search(r'delll: "([^"]+)"', response).group(1)
                    cookies = {'surl': surl, 'embx': f'["{email}"]'}
                    post('https://email-fake.com/del_mail.php', {'delll': delll}, cookies=cookies)
                    return tag
                else:
                    exception = TimeoutError("No message received")
                tags = soup.select('#email-table a')
                if len(tags) > 0:
                    return tags
            except (ConnectionError, ConnectTimeout):
                exception = ConnectionError("There is no internet connection")
        raise exception
    elif isinstance(email, Tag):
        start = time()
        exception = None
        while time() - start < timeout:
            try:
                print(url := f'https://www.email-fake.com{email.get("href")}')
                response = get(url).text
                soup = BeautifulSoup(response, 'html.parser')
                tag = soup.find('div', class_='mess_bodiyy')
                if tag:
                    return tag
            except ConnectionError:
                exception = ConnectionError("There is no internet connection")
        raise exception
    return None


def delete_all_messages(email: str):
    username, domain = email.split("@")
    surl = f'{domain}/{username}'
    response = get("https://email-fake.com/", cookies={'surl': surl}).text

    if match := re.search(r'delll: "([^"]+)"', response):
        delll = match.group(1)
        cookies = {'surl': surl, 'embx': f'["{email}"]'}
        post('https://email-fake.com/del_mail.php', {'delll': delll}, cookies=cookies)

    if match := re.search(r'dellall: "([^"]+)"', response):
        dellall = match.group(1)
        url = "https://email-fake.com/del_mail.php"
        headers = {
            'Cookie': f'surl={surl}; embx=["{email}"]'
        }
        payload = {
            "dellall": dellall
        }
        post(url, headers=headers, data=payload)
