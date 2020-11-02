#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
useful line processing tips for daily quick need
Created on Sun Oct 11 20:52:26 2020
@author: wuulong
"""
import os
import os.path
import zipfile
import re
from urllib.parse import quote
import pandas as pd 
import requests
import json
import time

#%% load file contents to lines
def file_to_lines(pathname):
    fo = open(pathname, "r")
    #lines = fo.readlines()
    lines = fo.read().splitlines()
    fo.close()
    return lines

def url_get(filename,url):
    """
        get url to file
    """
    print("filename=%s,url=%s" %(filename,url))
    if not os.path.isfile(filename):
        r = requests.get(url, params = {})
        open(filename, 'wb').write(r.content)
        
def load_json(filename,case_id=0):
    """
        load json file and transfer to panda
        hardcode: handle json with data in 'data'  
        
    """
    with open(filename, 'r') as json_file:
        data_head = json.load(json_file)
    
    if case_id==1: # DrainageReport
        #may need to change related to data.
        data = data_head['Data']['FileList']
    else:
        data = data_head

    if len(data)>0:
        cols = data[0].keys()
    else:
        return None
        
    
    out = []
    for row in data:
        item = []
        for c in cols:
            item.append(row.get(c, {}))
        out.append(item)

    return pd.DataFrame(out, columns=cols)

def DrainageReport():
    """
        generate drainage report
    """
    page = 1 
    
    #global df_all
    df_all = None 
    """
All
https://rdi-123.wrap.gov.tw/Integration_WRPI_Drainage/FuncModule/Drainage_2018/DrainageReport.ashx?cmd=public&exist=1&coun=&key=&limit=100

中央管區域排水
https://rdi-123.wrap.gov.tw/Integration_WRPI_Drainage/FuncModule/Drainage_2018/DrainageReport.ashx?cmd=public&exist=1&level=%u4E2D%u592E%u7BA1%u5340%u57DF%u6392%u6C34&coun=&key=&limit=100

直轄市管區域排水
https://rdi-123.wrap.gov.tw/Integration_WRPI_Drainage/FuncModule/Drainage_2018/DrainageReport.ashx?cmd=public&exist=1&level=%u76F4%u8F44%u5E02%u7BA1%u5340%u57DF%u6392%u6C34&coun=&key=&limit=100

縣市管區域排水
https://rdi-123.wrap.gov.tw/Integration_WRPI_Drainage/FuncModule/Drainage_2018/DrainageReport.ashx?cmd=public&exist=1&level=%u7E23%u5E02%u7BA1%u5340%u57DF%u6392%u6C34&coun=&key=&limit=100

市區排水
https://rdi-123.wrap.gov.tw/Integration_WRPI_Drainage/FuncModule/Drainage_2018/DrainageReport.ashx?cmd=public&exist=1&level=%u5E02%u5340%u6392%u6C34&coun=&key=&limit=100

    """
    while True:
        urlbase = "https://rdi-123.wrap.gov.tw/Integration_WRPI_Drainage/FuncModule/Drainage_2018/DrainageReport.ashx?cmd=public&exist=1&coun=&key=&limit=100"
        url = "%s&page=%i" %(urlbase,page)
        file_datestr = "output/DrainageReport"
        filename = "%s_%04i.json" %(file_datestr,page)

        cont = True
        while cont:
            try:
                url_get(filename, url)
                df = load_json(filename,1)
                #df = pd.read_csv(filename) 
                
                cont = False
            except:
                print("Exception when process %s, retrying after 60s" %(filename))
                if os.path.isfile(filename):
                    os.remove(filename)
                time.sleep(60)
        
        if page>1:
            df_all = pd.concat([df_all,df])
        else:
            df_all = df
        page += 1
        if len(df.index)<100: # check if the last recoord
        #if page > 3:
            break
    filename = "%s.csv" %(file_datestr)
    print("%s saved" %(filename))
    df_all.to_csv(filename)

#%% diff 2 set 
def set_diff():
    #lines1=file_to_lines("/Users/wuulong/Downloads/river_id-rivercode.csv")
    #lines2=file_to_lines("/Users/wuulong/Downloads/river_code-riverpoly.csv")
    lines1=file_to_lines("/Users/wuulong/Downloads/river_name-rivercode.csv")
    lines2=file_to_lines("/Users/wuulong/Downloads/river_name-riverpoly.csv")

    s1 = set(lines1)
    s2 = set(lines2)
    print(len(s2.difference(s1)))
    #print(s1.difference(s2))

#%% formated output
def shp_tosql():
    lines=file_to_lines("shp.txt")
    for line in lines:
        #print(line,end = '')
        basename = os.path.basename(line)
        base = os. path. splitext(basename)[0]
        
        out1 = "shp2pgsql -W UTF-8 -D -I %s > /tmp/%s.sql" %(line,base)
        out2 = "psql -p 5431 -U postgres -d postgis -f /tmp/%s.sql" %(base)
        print("#processing file:%s\n%s\n%s" %(line,out1,out2))


# generate pyqgis csv import script
def csvlist_to_pyqgis():
    lines=file_to_lines("csv.txt") #csv file list
    #lines=file_to_lines("/tmp/kml.txt") #kml fail, not work
    #group define file
    group_df = pd.read_csv("group.txt") #group define fiile
    #dataset_id    架構分類
    for line in lines:
        #print(line,end = '')
        #print("line=%s" %(line))
        basename = os.path.basename(line)
        
        base = os. path. splitext(basename)[0]
        #36689-河川復育英文版新聞
        cols = base.split("-")
        dataset_id = int(cols[0])
        #print("dataset_id=%i" %(dataset_id))
        group_names = group_df[group_df['dataset_id']==dataset_id]['架構分類'].values.tolist()
        if len(group_names)>0:
            group_name = group_names[0]
        else:
            group_name = ""
        par="&geomType=none"
        #line_encoded = urllib.quote(line)
        line_encoded = quote(line) 
        
        script_str = "[\"%s\",\"%s\",\"%s\",\"%s\"]," %(line_encoded,base,par,group_name) #CSV
        #script_str = "[\"%s\",\"%s\",\"%s\"]," %(line_encoded,base,group_name) #KML
        print(script_str)

# unzip files in dir, pack for qgis wra_opendata project need 
def unzip_zips_indir(search_dir):
    #解 zip
    
    #setup
    extract_dir =  "%s/tmp" %(search_dir)
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)
    target_dir="%s/zip" %(search_dir)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    for dirpath, dirnames, filenames in os.walk(search_dir):
        #print("dirpath=%s\ndirnames=%s\nfilenames=%s" %(dirpath, dirnames, filenames))
        for filename in [f for f in filenames if f.endswith(".zip")]: #"25776-水庫堰壩位置圖.zip"
            zip_file = os.path.join(dirpath, filename)   
            
            #extract zip
            print("extracting %s" %(zip_file))
            with zipfile.ZipFile(zip_file,"r") as zip_ref:
                zip_ref.extractall(extract_dir) 
            dirs = os.listdir(extract_dir)
            basename = os.path.basename(zip_file)    
            base = os. path. splitext(basename)[0] 
            
            if os.path.isdir(dirs[0]):
                old_path = "%s/%s" %(extract_dir,dirs[0])
                new_path = "%s/%s-%s" %(target_dir,base,dirs[0]) 
                if os.path.isdir(old_path): 
                    os.rename(old_path,new_path)
                #else:
                #    print("%s not normal format, dirs=%s" %(zip_file,str(dirs)))
            else:
                #move all to new dir    
                ename = os. path. splitext(dirs[0])[0]
                new_path = "%s/%s-%s" %(target_dir,base, ename) 
                if not os.path.exists(new_path):
                    os.makedirs(new_path)
                for file in dirs:
                    old_path = "%s/%s" %(extract_dir,file)
                    new_file = "%s/%s" %(new_path,file)
                    os.rename(old_path,new_file)
            print("done %s" %(zip_file))
            #time.sleep(3)
#%% shp file list 轉換成 pyqgis script
def gen_pyqgis_script():
    #["./BASIN/basin/basin.shp","BASIN-河川流域範圍圖"]
    #./zip/25780-河川支流-riverlin/riverlin/riverlin.shp
    lines=file_to_lines("/tmp/shps.txt")
    for line in lines:
        #print(line,end = '')
        cols = line.split("/")
        name = cols[2]
        #basename = os.path.basename(line)
        #base = os. path. splitext(basename)[0]
        
        out1 = "[\"%s\",\"%s\"]," %(line,name)
        print(out1)
def walk_dir(search_dir):
    
    for dirpath, dirnames, filenames in os.walk(search_dir):
        #print("dirpath=%s\ndirnames=%s\nfilenames=%s" %(dirpath, dirnames, filenames))
        for filename in [f for f in filenames if f.endswith(".shp")]:
            print(os.path.join(dirpath, filename))    
            
#zip_file = "%s/%s" % ("/Users/wuulong/MakerBk/QGIS/projects/wra_opendata","32722-中央管水門.zip")
#out_tmp3(zip_file)
#unzip_zips_indir("/Users/wuulong/MakerBk/QGIS/projects/wra_opendata")
#gen_pyqgis_script()
#csvlist_to_pyqgis()
#gen_pyqgis_script()
DrainageReport()
"""
url='https://data.coa.gov.tw/service/opendata/OpenDataServiceList.aspx'
file_in = 'output/coa_opendata.json'
file_out = 'output/coa_opendata.csv'
url_get(file_in,url)
df = load_json(file_in)
df.to_csv(file_out)
"""

