import requests
from bs4 import BeautifulSoup


class File:
    def __init__(self, file_id):
        self.normal_download_link = f'https://www.mediafire.com/file/{file_id}/'

    def __response__(self):
        soup = BeautifulSoup(requests.get(self.normal_download_link).text, 'html.parser')
        url = soup.find('a', attrs={'aria-label': "Download file"}).get('href')
        return requests.get(url)

    def content(self):
        return self.__response__().content

    def text(self):
        return self.__response__().text
