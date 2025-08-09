import json
from json import JSONDecodeError
from typing import Union, Mapping, Any, Iterable, Tuple

from autowebx import var_name


class AutoSaveDict(dict):
    def __init__(self, file_path: str = 'dict.json'):
        self.__file_path = file_path
        try:
            super().__init__(json.load(open(self.__file_path, 'r', encoding='utf-8')))
        except (FileNotFoundError, JSONDecodeError):
            super().__init__()

        self.__save()

    def __save(self, ):
        json.dump(self, open(self.__file_path, 'w', encoding='utf-8', errors='ignore'), indent=2, ensure_ascii=False)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.__save()

    def __delitem__(self, key):
        super().__delitem__(key)
        self.__save()

    def update(
            self,
            __m: Union[Mapping[Any, Any], Iterable[Tuple[Any, Any]]] = (),
            **kwargs: Any
    ) -> None:
        """
        يغطّي حالتين أساسيتين:
        1. update(dict_or_mapping)
        2. update([(k1, v1), (k2, v2), ...], key=value, ...)
        """
        # أولًا: ننفّذ وظيفة الـ dict الأصلية (ترحيل القيم)
        super().update(__m, **kwargs)
        # بعد ذلك: نحفظ القاموس في المِلَفّ
        self.__save()

    def clear(self):
        super().clear()
        self.__save()

    def __call__(self, key, from_list: list = None, loop: bool = False):
        answer = self.setdefault(key, 0)
        if isinstance(answer, int):
            if from_list is not None:
                if answer < len(from_list):
                    self[key] = answer + 1
                    return from_list[answer]
                else:
                    if loop:
                        self[key] = 0
                        if len(from_list) > 0:
                            return self(key, from_list, loop)
                        else:
                            raise IndexError(f"The list {var_name(from_list)} is empty")
                    else:
                        raise IndexError('IndexError: list index out of range')
            else:
                self[key] = answer + 1
                return answer
        else:
            return answer

    def get(self, __key, default=None, mandatory=True):
        if not (result := super().get(__key, default)) and mandatory:
            self[__key] = input(__key + ': ')
        return result