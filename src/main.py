import datetime

from src.util.mysqlclient import MySqlClient
from src.util.get_data import GetData

if __name__ == '__main__':
    mysql_client = MySqlClient()
    today = datetime.date.today()

    for i in range(70):
        GetData.get_future(mysql_client, today, GetData.HSI_FUTURE)
        GetData.get_option(mysql_client, today, GetData.HSI_OPTION, 4)
        today = today - datetime.timedelta(days=1)
