#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze power generation data examples 
@author: wuulong
"""

#%% 
import pandas as pd 
import pandasql as ps
# 讀取發電歷史資料
power_df = pd.read_csv("power_generation.csv")
#找某個機組
query_str = """SELECT * FROM power_df where 機組名稱 ='興達#1'"""
m1_df= ps.sqldf(query_str, locals())
print(m1_df.head(2))

#根據機組累加發電量
query_str = """SELECT 機組名稱,sum(淨發電量) FROM power_df group by 機組名稱 order by sum(淨發電量) desc"""
m1_df= ps.sqldf(query_str, locals())
print(m1_df.head(2))

#找某個時間
query_str = """SELECT * FROM power_df where 時間 = '2020-04-14 22:50'"""
m1_df= ps.sqldf(query_str, locals())
print(m1_df.head(2))


#每天的加總
query_str = """SELECT strftime('%Y-%m-%d',時間) 日期,sum(淨發電量) FROM power_df group by 日期"""
m1_df= ps.sqldf(query_str, locals())
print(m1_df.head(2))

#找某一天，某一個月
query_str = """SELECT *,strftime('%Y-%m-%d',時間) 日期 FROM power_df where 日期='2020-04-15'"""
m1_df= ps.sqldf(query_str, locals())
print(m1_df.head(2))

#根據以前的查詢結果，繼續分析
query2_str = """SELECT 類別,sum(淨發電量) 發電量  FROM m1_df group by 類別 order by 發電量 desc"""
m2_df= ps.sqldf(query2_str, locals())
print(m2_df.head(2))

#輸出成 csv
m1_df = m1_df.drop(['日期'], axis=1) #有需要的話，可以刪除過程中長出的欄位
m1_df.to_csv('power_20200415.csv')

#%%
# 
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
myfont = FontProperties(fname=r'/Library/Fonts/Microsoft/MingLiU.ttf')
m2_df.plot('類別',y='發電量',kind='barh',use_index=True) #line type have problem
plt.title("類別發電量",fontproperties=myfont) 
plt.ylabel('淨發電量',fontproperties=myfont,size=6)
plt.xlabel('類別',fontproperties=myfont,size=6)
plt.legend(prop=myfont)
plt.xticks(fontname = 'SimSun',size=10)
plt.yticks(fontname = 'SimSun',size=10)
plt.show()

#%% useful hint
#power_df.columns 