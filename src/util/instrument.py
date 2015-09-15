from enum import Enum
import re
import datetime

class InstrumentType(Enum):
    Call = 'C'
    Put = 'P'


class Instrument:
    def __init__(self):
        self.date = ''
        self.instrument = ''
        self.contract_month = ''
        self.instrument_type = InstrumentType.Call
        self.strike = 0
        self.open_t = 0
        self.high_t = 0
        self.low_t = 0
        self.volume_t = 0
        self.close_t = 0
        self.total_volume = 0
        self.open_interest = 0
        self.change_close = 0
        self.change_open_interest = 0

    def __init__(self, dt, instr, row, type=InstrumentType.Call, strike=0):
        self.date = dt.strftime("%Y%m%d")
        self.instrument = instr
        self.instrument_type = type
        self.strike = strike

        # Future
        if type == InstrumentType.Call and strike == 0:
            self.contract_month = row[0]

            for index, val in enumerate(re.sub(r'\s+', r' ', row[2]).split(' ')):
                val = val.replace('\\r', '').replace('\\r', '')
                if index == 0:
                    self.open_t = int(val)
                elif index == 1:
                    self.high_t = int(val)
                elif index == 2:
                    self.low_t = int(val)
                elif index == 3:
                    self.volume_t = int(val)
                elif index == 4:
                    self.close_t = int(val)
                elif index == 5:
                    self.change_close = int(val)
            for index, val in enumerate(re.sub(r'\s+', r' ', row[3]).split(' ')):
                val = val.replace('\\r', '').replace('\\n', '')
                if index == 2:
                    self.total_volume = int(val)
                elif index == 3:
                    self.open_interest = int(val)
                elif index == 4:
                    self.change_open_interest = int(val)
        elif strike > 0:
            self.contract_month       = row[0]
            self.open_t               = int(row[3])
            self.high_t               = int(row[4])
            self.low_t                = int(row[5])
            self.close_t              = int(row[6])
            self.change_close         = int(row[7]) if row[7] != '-' else 0
            self.volume_t             = int(row[8])
            self.total_volume         = int(row[8])
            self.open_interest        = int(row[9])
            self.change_open_interest = int(row[10]) if row[10] != '-' else 0


