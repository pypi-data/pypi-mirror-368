from ...interface import IPacker
from typing import Tuple


class SaveInstrumentParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return (list(self._obj.DataList))

    def tuple_to_obj(self, t):
        if len(t) >= 1:
            self._obj.DataList = t[0]

            return True
        return False
