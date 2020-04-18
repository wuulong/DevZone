#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: Get iNaturalist data by API, then become SQL to process
@author: wuulong
doc: https://forum.inaturalist.org/t/how-to-use-inaturalists-search-urls-wiki/63
"""

#%%
import requests 
def url_to_file(url,pathname,reload=False):
    print("url_to_file: url=%s, pathname=%s" %(url,pathname))
    need_load= True
    if reload==False and os.path.isfile(pathname) :
        need_load = False
    if need_load:
        r = requests.get(url, allow_redirects=True,verify=False)
        open(pathname, 'wb').write(r.content)



#%% 
url="https://www.inaturalist.org/observations.csv?user_id=2760716"
pathname="ob_result.csv"
url_to_file(url,pathname)

#%% 
import pandas as pd 
import pandasql as ps
# 讀取發電歷史資料
ob_df = pd.read_csv("ob_result.csv")
#列表
query_str = """SELECT * FROM ob_df"""
m1_df= ps.sqldf(query_str, locals())
print(m1_df.head(2))