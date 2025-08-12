from typing import List
from ...interface import IData
from ...packer.trade.save_instrument_param_data_packer import SaveInstrumentParamDataPacker
from .instrument_data import InstrumentData


class SaveInstrumentParamData(IData):
    def __init__(self):
        super().__init__(SaveInstrumentParamDataPacker(self))
        self._DataList: List[InstrumentData] = []

    @property
    def DataList(self):
        return self._DataList

    @DataList.setter
    def DataList(self, value: List[InstrumentData]):
        self._DataList = value
