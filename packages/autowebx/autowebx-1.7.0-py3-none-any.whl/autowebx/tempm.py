import re
from time import time
from bs4 import BeautifulSoup, Tag, ResultSet
from requests import get, post


def get_suggestions():
    html = get("https://tempm.com/").text
    soup = BeautifulSoup(html, "html.parser")
    return [child.text for child in soup.find('div', class_="tt-suggestions").children]


def get_message(email: str, timeout: int | float = 30) -> Tag | ResultSet[Tag]:
    url = "https://tempm.com/"
    username, domain = email.split("@")
    surl = f'{domain}/{username}'
    start = time()
    exception = None
    while time() - start < timeout:
        try:
            response = get(url, cookies={'surl': surl})
            soup = BeautifulSoup(response.text, 'html.parser')
            tag = soup.find('div', class_='mess_bodiyy')
            if tag:
                delll = re.search(r'delll: "([^"]+)"', response.text).group(1)
                cookies = {'surl': surl, 'embx': f'["{email}"]'}
                post('https://tempm.com/del_mail.php', {'delll': delll}, cookies=cookies)
                return tag
            else:
                exception = TimeoutError("No message received")
            tags = soup.select('#email-table a')
            if len(tags) > 0:
                return tags
        except ConnectionError:
            exception = ConnectionError("There is no connection")
    raise exception
