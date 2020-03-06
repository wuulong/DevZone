#purbao data to GIS
#need output sub directory
#set default parameter if needed, default for all taiwan with level 0 data
#modify time period for you need.
import requests
import json
import os
import pandas as pd
from datetime import timedelta, datetime
import time
"""
purbao URL format and example
url = "http://purbao.lass-net.org/sensorGrid?date=2017/5/28&hour=0&level=0&minLat=23&maxLat=23.5&minLng=120&maxLng=121"
date_str="2017/5/2"
hour = 0
level=0
minLat=23
maxLat=23.5
minLng=120
maxLng=121

API Output
{"level":0,"data":[{"gridX":"120.08","gridY":"23.18","time":"0:0:0","pm25":30},{"gridX":"120.08","gridY":"23.18","time":"0:10:0","pm25":32},
"""
# setting for data range and level
level=0
minLat=21.81
maxLat=25.37
minLng=118.17
maxLng=122.04
def pm25_day(data_date):

    url_fmt = "http://purbao.lass-net.org/sensorGrid?date=%s&hour=%i&level=%i&minLat=%f&maxLat=%f&minLng=%f&maxLng=%f" 
    
    df_all = None
    date_str = "%s/%s/%d" %( data_date.year, data_date.month, data_date.day )
    for hour in range(24):
        url = url_fmt %(date_str,hour,level,minLat,maxLat,minLng,maxLng)
        file_datestr = data_date.strftime("%Y%m%d")
        filename = "output/R%s_%02i:00.json" %(file_datestr,hour)
        #print("filename=%s, url=%s" %(filename, url))
        cont = True
        while cont:
            try:
                pm25_get(filename, url)
                df = load_json(filename)
                cont = False
            except:
                print("Exception when process %s, retrying after 60s" %(filename))
                if os.path.isfile(filename):
                    os.remove(filename)
                time.sleep(60)
        df['datetime']="%s %02i:00" %(file_datestr,hour)
        
        if hour>0:
            df_all = pd.concat([df_all,df])
        else:
            df_all = df
    filename = "output/D%s.csv" %(file_datestr)
    print("day saved %s, shape = %s" %(filename, str(df_all.shape)))
    df_all.to_csv(filename)
    
    df_all=df_all.astype({'pm25': 'float64'})
    df_mean = df_all.groupby(['gridX','gridY'])['pm25'].mean() 
    df_mean.columns = ['gridX','gridY','pm25']
    filename = "output/DD%s.csv" %(file_datestr)
    print("Day saved %s, shape = %s" %(filename, str(df_mean.shape)))
    df_mean = df_mean.reset_index()
    df_mean.to_csv(filename,header=True,float_format="%.2f")
    
    return df_mean
        
def pm25_get(filename,url):
    if not os.path.isfile(filename):
        r = requests.get(url, params = {})
        open(filename, 'wb').write(r.content)
def load_json(filename):
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
    cols = ['gridX','gridY','time','pm25']
    
    out = []
    for row in data['data']:
        item = []
        for c in cols:
            item.append(row.get(c, {}))
        out.append(item)

    return pd.DataFrame(out, columns=cols)

def pm25_range(start_str,end_str):
    start_date = datetime.strptime(start_str, "%Y/%m/%d")
    end_date = datetime.strptime(end_str, "%Y/%m/%d")

    df_month = None
    first_day = True
    start_month = start_date.month
    date_now = start_date
    df_all = None
    while True:
        
        if date_now.day>32:
            pass
        else:
            if date_now > end_date:
                break
            month = date_now.month
            year = date_now.year
            file_datestr = date_now.strftime("%Y%m")
            df = pm25_day(date_now)
            df['datetime']="%s" %(date_now.strftime("%Y/%m/%d"))
            if first_day:
                df_all = df
                first_day = False
            else:
                df_all = pd.concat([df_all,df])

        date_now += timedelta(days=1)
        if not month == date_now.month: #will cross month
            
            filename = "output/M%s.csv" %(file_datestr)
            print("month saved %s, shape = %s" %(filename, str(df_all.shape)))
            df_all.to_csv(filename,header=True,float_format="%.2f")
            
            df_all = df_all.reset_index()
            df_all=df_all.astype({'pm25': 'float64'})
            
            df_mean = df_all.groupby(['gridX','gridY'])['pm25'].mean()
            df_mean = df_mean.reset_index()
            df_mean.columns = ['gridX','gridY','pm25']
            filename = "output/MM%s.csv" %(file_datestr)
            print("Month saved %s, shape = %s" %(filename, str(df_mean.shape)))
            df_mean.to_csv(filename,header=True,float_format="%.2f")
            first_day = True
            df_all = None

def pm25_gen_year(year):

    df_all = None
    first_month = True
    
    for month in range(1,13):
        filename = "output/MM%i%02i.csv" %(year,month)
        print("filename=%s" %(filename))
        if os.path.isfile(filename):
            print("read_csv: %s" %(filename))
            df = pd.read_csv(filename)
            df['month']="%i%02i" %(year,month)
            print(df.shape)
            
            if first_month:
                df_all = df
                first_month = False
            else:
                df_all = pd.concat([df_all,df])

    filename = "output/Y%i.csv" %(year)
    print("year saved %s, shape = %s" %(filename, str(df_all.shape)))
    df_all.to_csv(filename,header=True,float_format="%.2f")
    df_all=df_all.astype({'pm25': 'float64'})
    df_mean = df_all.groupby(['gridX','gridY'])['pm25'].mean()
    df_mean.reset_index()
    df_mean.columns = ['gridX','gridY','pm25']
    filename = "output/YY%i.csv" %(year)
    print("Year saved %s, shape = %s" %(filename, str(df_mean.shape)))
    df_mean.to_csv(filename,header=True,float_format="%.2f")

#pm25_day(datetime.strptime("2019/03/04", "%Y/%m/%d")) # get one day data for debug
df_all = pm25_range("2019/01/27","2020/01/01") # get day,month data for periold of time
pm25_gen_year(2019) #get year data after month data ready