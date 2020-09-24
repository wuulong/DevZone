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
        #url =  "https://opendata.epa.gov.tw/webapi/api/rest/datastore/355000000I-001255?filters=SampleDate ge '%s' and SampleDate lt '%s' &sort=SampleDate&offset=%i&limit=1000&format=csv" % (start_str, end_str, offset) 
        #url = "http://opendata.epa.gov.tw/webapi/Data/WQXRiver/?$filter=ItemName%20eq%20%27%E6%B2%B3%E5%B7%9D%E6%B1%A1%E6%9F%93%E5%88%86%E9%A1%9E%E6%8C%87%E6%A8%99%27&$orderby=SampleDate%20desc&$skip=%i&$top=1000&format=csv" %(offset)
        url = "https://opendata.epa.gov.tw/webapi/api/rest/datastore/355000000I-001255?filters=ItemName eq '河川污染分類指標'&sort=SampleDate&offset=%i&limit=1000&format=csv" %(offset)
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
                time.sleep(60)
        
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


#%%
# generate value diff field 
def proc_diff():
    filename = "output/WaterQuality_1950-01-01_2020-12-31.csv"
    df = pd.read_csv(filename)
    df_sorted = df.sort_values(by=['County','SiteName','SampleDate'])
    sitename_prev = ""
    value_prev = 0
    valid_prev = True
    for index, row in df_sorted.iterrows():
        
        valid=True
        if row['ItemValue'] =='-':
            valid = False
        else:
            try:
                value = float(row['ItemValue'])
            except:
                value = 0
        
        
        if row['SiteName']!= sitename_prev:
            diff_value = 0
            sitename_prev = row['SiteName']
            
        else:
            if valid==False or value_prev==False:
                diff_value = 0
            else:
                diff_value = value - value_prev
        
        value_prev = value
        valid_prev = valid
        
        #row['ValueDiff']=diff_value
        df_sorted.loc[index, 'ValueDiff'] = diff_value
        #print("%s-%s" %(index,row))

    df_sorted.to_csv("output/WaterQuality_1950-01-01_2020-12-31_diff.csv")
proc_diff()
#water_quality('2020-06-01','2020-07-01')
#print("Start time: %s " %(datetime.now()))
#water_quality('2019-07-01','2020-07-01')
#water_quality('1950-01-01','2020-12-31')
#water_quality('2020-06-01','2020-07-01')
#print("End time: %s " %(datetime.now()))