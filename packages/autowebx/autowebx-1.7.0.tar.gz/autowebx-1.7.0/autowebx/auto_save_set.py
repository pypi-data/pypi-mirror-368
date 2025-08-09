from autowebx.files import load


class AutoSaveSet(set):
    def __init__(self, filename):
        super().__init__(load(filename))
        self.filename = filename
        self._save_to_file()

    def _save_to_file(self):
        open(self.filename, 'w').write('\n'.join(self))

    def add(self, element):
        super().add(element)
        self._save_to_file()

    def remove(self, element):
        super().remove(element)
        self._save_to_file()

    def update(self, *args):
        super().update(*args)
        self._save_to_file()

    def discard(self, element):
        super().discard(element)
        self._save_to_file()

    def clear(self):
        super().clear()
        self._save_to_file()

    def pop(self):
        element = super().pop()
        self._save_to_file()
        return element

    def difference_update(self, *args):
        super().difference_update(*args)
        self._save_to_file()

    def intersection_update(self, *args):
        super().intersection_update(*args)
        self._save_to_file()

    def symmetric_difference_update(self, *args):
        super().symmetric_difference_update(*args)
        self._save_to_file()

    def __iadd__(self, elements):
        super().update(elements)
        self._save_to_file()
        return self
