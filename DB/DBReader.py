import pandas as pd
import pymysql
from datetime import datetime
from datetime import timedelta
import re
import json

with open('env.json', 'r') as f:
    config = json.load(f)

host = config['dbprivate']["host"]
user = config['dbprivate']["user"]
password = config['dbprivate']["password"]
db = config['dbprivate']["db"]


class pricereader:
    def __init__(self):
        """Connect MariaDB and create stock code dictionary"""
        self.conn=pymysql.connect(host=host, user=user, password=password, db=db, charset='utf8')
        self.codes={}
        self.get_comp_info()
    
    def __del__(self):
        """Disconnect MariaDB"""
        self.conn.close()

    def get_comp_info(self):
        """read company_info table and save the data to codes"""
        sql = "SELECT * FROM company_info"
        krx = pd.read_sql(sql, self.conn)
        for idx in range(len(krx)):
            self.codes[krx['code'].values[idx]] = krx['company'].values[idx]

    

    def get_daily_price(self, code, start_date=None, end_date=None):
        """return daily price DataFrame"""
        if start_date is None:
            start_date = datetime.today().strftime('%Y-%m-%d')
            print("start_date is initialized to {}".format(start_date))
        else:
            start_lst = re.split('\D+', start_date)
            start_year = int(start_lst[0])
            start_month = int(start_lst[1])
            start_day = int(start_lst[2])
            start_date = f"{start_year:04d}-{start_month:02d}-{start_day:02d}"

        if end_date is None:
            end_date = datetime.today().strftime('%Y-%m-%d')
            print("end_date is initialized to {}".format(end_date))
        else:
            end_lst = re.split('\D+', end_date)
            end_year = int(end_lst[0])
            end_month = int(end_lst[1])
            end_day = int(end_lst[2])
            end_date = f"{end_year:04d}-{end_month:02d}-{end_day:02d}"

        codes_keys = list(self.codes.keys())
        codes_values = list(self.codes.values())

        if code in codes_keys:
            pass
        elif code in codes_values:
            idx = codes_values.index(code)
            code = codes_keys[idx]
        else:
            print("ValueError: Code '{}' does not exist.".format(code))
    

        sql = f"SELECT * FROM daily_price WHERE code='{code}' and date >= '{start_date}' and date <= '{end_date}'"
        df = pd.read_sql(sql, self.conn)
        df.index = df['date']
        return df


