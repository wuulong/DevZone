#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
README: 環保署水質 API 多次下載打包工具
Logic: 
    1. CSV 多次下載成本地檔案
    2. 讀檔成 pd, 合併成全部的 CSV
Filename: WaterQuality_startdate_enddate[_offset].csv
@author: wuulong
"""

import requests
import os
import pandas as pd
from datetime import timedelta, datetime
import time

# date format: 2020-06-01
def water_quality(start_str, end_str):
    offset = 0 
    
    #global df_all
    df_all = None 
    while True:
        url =  "https://opendata.epa.gov.tw/webapi/api/rest/datastore/355000000I-001255?filters=SampleDate ge '%s' and SampleDate lt '%s' &sort=SampleDate&offset=%i&limit=1000&format=csv" % (start_str, end_str, offset) 
   
        file_datestr = "output/WaterQuality_%s_%s" %(start_str,end_str)
        filename = "%s_%04i.csv" %(file_datestr,offset)

        cont = True
        while cont:
            try:
                url_get(filename, url)
                df = pd.read_csv(filename) 
                
                cont = False
            except:
                print("Exception when process %s, retrying after 60s" %(filename))
                if os.path.isfile(filename):
                    os.remove(filename)
                time.sleep(10)
        
        if offset>0:
            df_all = pd.concat([df_all,df])
        else:
            df_all = df
        offset += 1000
        if len(df.index)<1000: # check if the last recoord
            break
    filename = "%s.csv" %(file_datestr)
    print("%s saved" %(filename))
    df_all.to_csv(filename)
    

def url_get(filename,url):
    if not os.path.isfile(filename):
        print("Getting %s to %s" %(url,filename))
        t1 = datetime.now()
        r = requests.get(url, params = {})
        open(filename, 'wb').write(r.content)
        t2 = datetime.now()
        print("[%s]-%s" %(t2-t1,filename))

water_quality('2020-06-01','2020-07-01')
