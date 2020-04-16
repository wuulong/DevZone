#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dataset 8931 util: parse Power generation json files in directory, summary to csv output
@author: wuulong
"""
import os,fnmatch
import json
#%%

def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        files.sort()
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

#result = find('2020*.jsonl', 'output') 
#%% 0archive load json

def load_json(filename,exists):
    try:
        data_date = ""
        with open(filename , 'r', encoding='UTF-8') as json_file:
            data = json.load(json_file)
        #print(data)
        data_date = data['']
        print("%s:%s" %(filename,data_date))
        csvs = []
        if not data_date in exists:
            exists[data_date]=1
            aaData = data['aaData']
            for item in aaData:
                if not item[1]=='小計':
                    csvs.append("%s,%s,%s,%s,%s,%s,%s" % (data_date,item[0],item[1],item[2],item[3],item[4],item[5]))
        return "\n".join(csvs)
    except:
        print("%s:%s" %(filename,"EXCEPTION!"))
        return None
#%% can handle duplicate file
def load_jsons(filenames):
    df_all = None
    first = True
    csv_lines = "時間,類別,機組名稱,裝置容量,淨發電量,容量比,備註\n"
    exists = {}
    ok = 0
    for filename in filenames:
        lines = load_json(filename,exists)
        if lines:
            csv_lines += lines + "\n"
            ok += 1
    print("pass rate : %s/%s=%.1f%%" %(ok,len(filenames), float(ok)/len(filenames)*100))
    return csv_lines
#%%
filenames = find('001.*', '.') 
csvlines = load_jsons(filenames)
f= open("power_generation.csv","w+")
f.writelines(csvlines)
f.close()