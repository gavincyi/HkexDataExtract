import re
import urllib.request
import urllib.error
import traceback

from src.util.instrument import Instrument, InstrumentType


class GetData():
    HKEX_DOMAIN = 'http://www.hkex.com.hk/eng/stat/dmstat/dayrpt/'
    HSI_FUTURE = 'hsif'
    HSI_OPTION = 'hsio'
    HHI_FUTURE = 'hhif'
    HHI_OPTION = 'hhio'

    @staticmethod
    def get_future(db, date, instrument):
        link = "%s%s%s.htm" % (GetData.HKEX_DOMAIN, instrument, date.strftime("%y%m%d"))
        if len(db.select("SELECT * from %s where date = '%s' and instrument = '%s'" %
                                 (db.HISTORICAL_PX_TABLE,
                                  date.strftime("%Y%m%d"), instrument)).fetch_row()) == 0:
            try:
                future_data = str(urllib.request.urlopen(link).read()).split('\\r\\n')
                # Parsing example:
                #                   After-Hours Trading Session            |                Day Trading Session                 |                    Combined
                #                                                  |                                                    |
                # Contract  *Open  *Daily  *Daily  *Close  Volume  |   *Open  *Daily  *Daily  Volume  Settle-   Chg in  |*Contract*Contract   Volume      Open  Change in
                # Month     Price    High     Low   Price          |   Price    High     Low             ment     Setl  |     High      Low           Interest         OI
                #                                                  |                                    Price    Price  |
                #                                                  |                                                    |
                # AUG-15   21,782  22,134  21,768  22,097   3,795  |  22,226  22,249  21,946  10,780   21,965     +170  |   26,439   20,072   14,575    14,689    -11,680
                # found = re.findall('(\D{3}-\d{2})\s+(.*)\s+\|\s+(.*)\s+\|\s+(.*)\s+', future_data)
                found = [re.findall('(\D{3}-\d{2})\s+(.*)\s+\|\s+(.*)\s+\|\s+(.*\d+)', s) for s in future_data]
                found = [s for s in found if len(s) > 0]

                for row in found:
                    try:
                        ins = Instrument(date, instrument, [ele.replace(',', '').replace('\r', '') for ele in row[0]])
                        db.insert(db.HISTORICAL_PX_TABLE,
                                  db.HISTORICAL_PX_COLS,
                                  [(ins.date, ins.instrument, ins.contract_month, ins.instrument_type.value, ins.strike,
                                    ins.open_t, ins.close_t, ins.high_t, ins.low_t,
                                    ins.volume_t, ins.total_volume, ins.open_interest,
                                    ins.change_close, ins.change_open_interest)])
                    except ValueError:
                        print("Cannot decode the following:\n%s" % row)

                print ("Finished getting future data on <%s> %s" % (instrument, date.strftime("%d-%m-%Y")))
                return True

            except urllib.error.HTTPError:
                print ("No such business date <%s> %s" % (instrument, date.strftime("%d-%m-%Y")))
                return False
        else:
            print ("Data existed <%s> %s" % (instrument, date.strftime("%d-%m-%Y")))
            return False

    @staticmethod
    def get_option(db, date, instrument, num_of_months):
        front_months = []
        link = "%s%s%s.htm" % (GetData.HKEX_DOMAIN, instrument, date.strftime("%y%m%d"))
        if len(db.select("SELECT * from %s where date = '%s' and instrument = '%s'" %
                                 (db.HISTORICAL_PX_TABLE,
                                  date.strftime("%Y%m%d"), instrument)).fetch_row()) == 0:
            try:
                option_data = str(urllib.request.urlopen(link).read()).split('\\r\\n')

                # CONTRACT STRIKE*OPENING  *DAILY  *DAILY  O.Q.P.   O.Q.P.  IV%   VOLUME      OPEN    CHANGE
                # MONTH     PRICE   PRICE    HIGH     LOW   CLOSE   CHANGE                INTEREST     IN OI
                # SEP-15  12800 C       0       0       0    7836      -83   86        0       204         0
                found = [re.findall('(\D{3}-\d{2})\s+(\d+)\s+(C|P)\s+((?:\d|-|\+)+)' +
                                    '\s+((?:\d|-|\+)+)\s+((?:\d|-|\+)+)\s+((?:\d|-|\+)+)' +
                                    '\s+((?:\d|-|\+)+)\s+((?:\d|-|\+)+)\s+((?:\d|-|\+)+)' +
                                    '\s+((?:\d|-|\+)+)\s+((?:\d|-|\+)+).*', s) for s in option_data]
                found = [s for s in found if len(s) > 0]

                for row in found:
                    try:
                        ins = Instrument(dt=date, instr=instrument, row=row[0], type=InstrumentType(row[0][2]), strike=int(row[0][1]))
                        if len(front_months) < 4 and ins.contract_month not in front_months:
                            front_months.append(ins.contract_month)

                        if ins.contract_month in front_months:
                            db.insert(db.HISTORICAL_PX_TABLE,
                                      db.HISTORICAL_PX_COLS,
                                      [(ins.date, ins.instrument, ins.contract_month, ins.instrument_type.value, ins.strike,
                                        ins.open_t, ins.close_t, ins.high_t, ins.low_t,
                                        ins.volume_t, ins.total_volume, ins.open_interest,
                                        ins.change_close, ins.change_open_interest)])
                    except ValueError:
                        print("Cannot decode the following:\n%s" % row)
                        traceback.print_exc()

                print ("Finished getting option data on <%s> %s" % (instrument, date.strftime("%d-%m-%Y")))
                return True

            except urllib.error.HTTPError:
                print ("No such business date <%s> %s" % (instrument, date.strftime("%d-%m-%Y")))
                return False
        else:
            print ("Data existed <%s> %s" % (instrument, date.strftime("%d-%m-%Y")))
            return False


