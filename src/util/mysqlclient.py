import MySQLdb

class MySqlClient:
    HISTORICAL_PX_TABLE = "historical_px"
    HISTORICAL_PX_COLS = ["date", "instrument", "month", "type", "strike", "op_t", "cl_t", "high_t", "low_t",
                          "vol_t", "total_vol", "oi", "chg_cl", "chg_oi"]


    def __init__(self):
        self.db = MySQLdb.connect(host="localhost",
                                 user="root",
                                 passwd="iver101",
                                 db="hkex")
    def insert(self, table, cols, rows):
        c = self.db.cursor()
        statement = "INSERT INTO %s (%s) VALUES (%s)" % (table, ",".join(cols), ",".join(["%s"] * len(cols)))
        c.executemany(
            statement, rows
        )
        self.db.commit()

    def select(self, stmt):
        self.db.query(stmt)
        result = self.db.use_result()
        return result


def InsertTest():
    mysql_client = MySqlClient()
    mysql_client.insert(mysql_client.HISTORICAL_PX_TABLE, mysql_client.HISTORICAL_PX_COLS,
                        [("20150101", "JAN-15", "C", 25000, 100, 100, 100, 100, 10000, 10000, 1200, -10, -10),
                         ("20150101", "JAN-15", "C", 25000, 100, 100, 100, 100, 10000, 10000, 1200, -10, -10)
                         ])

def SelectTest():
    mysql_client = MySqlClient()
    result = mysql_client.select("SELECT * from %s where date = '%s'" % (mysql_client.HISTORICAL_PX_TABLE, "20150901"))
    print(result)


if __name__ == '__main__':
    SelectTest()
