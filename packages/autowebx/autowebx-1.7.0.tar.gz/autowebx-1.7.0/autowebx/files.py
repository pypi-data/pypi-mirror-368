from threading import Lock, Thread, Condition

__lock = Lock()


def add(text: str, to: str) -> None:
    __lock.acquire()
    open(to, 'a').write(text)
    __lock.release()


def load(*paths: str) -> list[str] | list[list[str]]:
    lists = []
    for file_name in paths:
        try:
            lists.append(open(file_name, 'r').read().strip().split('\n'))
        except FileNotFoundError:
            open(file_name, 'w').write('')
            lists.append([])
    return lists if len(lists) > 1 else lists[0]


def replace(old: str, new: str, path: str) -> None:
    with __lock:
        old_content = open(path, 'r').read()
    new_content = old_content.replace(old, new)
    with __lock:
        open(path, 'w').write(new_content)


class File:
    def __init__(self, path: str) -> None:
        self.__path = path
        with open(self.__path, 'r') as file:
            self.__buffer = file.read()
        self.__changed = False
        self.__closed = False
        self.__lock = Lock()
        self.__condition = Condition(self.__lock)
        self.lines = self.__buffer.split('\n')
        self.__thread = Thread(target=self.__update, daemon=True)
        self.__thread.start()

    def __update(self):
        while True:
            with self.__condition:
                while not self.__changed and not self.__closed:
                    self.__condition.wait()
                if self.__closed:
                    break
                if not self.__buffer.strip():  # Avoid writing empty content
                    continue
                with open(self.__path, 'w') as file:
                    file.write(self.__buffer)
                self.__changed = False

    def replace(self, old: str, new: str) -> None:
        with self.__condition:
            self.__buffer = self.__buffer.replace(old, new)
            self.lines = self.__buffer.split('\n')
            self.__changed = True
            self.__condition.notify()

    def add(self, text: str) -> None:
        with self.__condition:
            self.__buffer += text
            self.lines = self.__buffer.split('\n')
            self.__changed = True
            self.__condition.notify()

    def close(self) -> None:
        with self.__condition:
            if not self.__closed:
                with open(self.__path, 'w') as file:
                    file.write(self.__buffer)
                self.__closed = True
                self.__condition.notify()
        self.__thread.join()

    def __del__(self):
        if not self.__closed:
            self.close()
