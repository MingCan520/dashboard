import requests
import re
import json
import pandas as pd

FMT = "https://www.timeanddate.com/weather/usa/new-york/historic?month=%d&year=%d"

patter = re.compile(r'<script type="text/javascript">\nvar data=(.*?);window.month=')


def fetch(month: int, year: int):
    url = FMT % (month, year)
    r = requests.get(url)
    json_str = patter.search(r.text).groups()[0]
    return json.loads(json_str)['detail']


def fetch_all():
    ret = []
    for year in range(2019, 2021):
        for month in range(1, 13):
            for item in fetch(month, year):
                if 'hl' in item:
                    # hl is the summary of a day, skip it
                    continue
                if item['desc'] == 'No weather data available':
                    # skip corrupt data
                    continue
                temp_hi = item['temp']
                temp_low = item['templow']
                weather = item['desc'].split('.')[0]
                t_stamp = int(item['date']) // 1000
                if item['ts'] == '06:00':
                    clock = 6
                elif item['ts'] == '12:00':
                    clock = 12
                elif item['ts'] == '18:00':
                    clock = 18
                else:
                    # skip corrupt data
                    continue
                ret.append({'temp_hi': temp_hi,
                            'temp_low': temp_low,
                            'weather': weather,
                            't_stamp': t_stamp,
                            'clock': clock, })
    return ret


# gather data and save to data.csv
df = pd.DataFrame(fetch_all())
df.to_csv('data.csv', index=False)
