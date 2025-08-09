import random


# noinspection HttpUrlsUsage
class Proxy:
    def __init__(
            self, text: str
    ):
        info = text.split('@')
        if len(info) == 2:
            authentication_information, self.server = info
            self.username, self.password = authentication_information.split(':')
        else:
            info = text.split(':')
            if len(info) == 2:
                self.username = self.password = None
                self.server = text
            elif len(info) == 4:
                self.username = info[2]
                self.password = info[3]
                self.server = f'{info[0]}:{info[1]}'
            else:
                raise TypeError(f"""Proxy must have one of the following formats:
                                    username:password@proxyserver:port
                                    proxy-server:port:username:password
                                    proxy-server:port
                                """)

    def for_requests(self):
        if self.username and self.password:
            server = f'http://{self.username}:{self.password}@{self.server}'
        else:
            server = f'http://{self.server}'
        return {"http": server, 'https': server}

    def for_playwright(self):
        return {
            'server': f'http://{self.server}',
            'username': self.username,
            'password': self.password,
        } if self.username and self.password else {'server': f'http://{self.server}'}


class LunaProxy(Proxy):
    __host_prefixes = ['pr', 'as', 'eu', 'na']

    def __init__(self, username: str, password: str, region: str | None = None, session_time: int = 3):
        super().__init__('0:0')
        self.username = f'user-{username}{f"-region-{region}" if region else ""}-sesstime-{session_time}'
        self.password = password
        self.server = f'{random.choice(LunaProxy.__host_prefixes)}.lunaproxy.com:12233'


if __name__ == '__main__':
    LunaProxy('khaled_L3yuV', 'bfdskjfsd456fD', 'ps')
