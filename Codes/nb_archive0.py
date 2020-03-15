#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 06:50:26 2020
Licence: MIT
@author: wuulong@gmail.com
"""

import os, fnmatch
import json
import pandas as pd 
import pandasql as ps
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

"""
Index(['producer_id', 'canonical_url', 'title', 'language', 'license',
       'published_at', 'first_seen_at', 'last_updated_at', 'hashtags', 'urls',
       'keywords', 'tags', 'comments', 'id', 'text'],
      dtype='object')
"""

#%%

def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

#result = find('2020*.jsonl', 'output') 
#%% 0archive load json

def load_json(filename):
    pos=0
    #fo = open(filename, "r")
    with open(filename) as f:
        out = []
        for line in f:
            data = json.loads(line)
            if pos==0:
                cols = list(data.keys())            
            
            item = []
            for row in data:
                if row in cols:
                    item.append(data[row])
            out.append(item)
                
            pos+=1            
    return pd.DataFrame(out, columns=cols)
#json_df = load_json('output/2020-02-01.jsonl')

#%%
def load_jsons(filenames):
    df_all = None
    first = True
    for filename in filenames:
        df = load_json(filename)
        if first:
            df_all = df
            first=False
        else:
            
            df_all = pd.concat([df_all,df])
    return df_all
#filenames = find('2020*.jsonl', 'output') 
#archive0_df = load_jsons(filenames)
#%% plot test
def plot_test(df,title):
    from matplotlib.font_manager import FontProperties
    myfont = FontProperties(fname=r'/Library/Fonts/Microsoft/MingLiU.ttf')
    df.plot('name',y='cnt',kind='barh') #line type have problem
    plt.title(title)
    #plt.ylabel('行業別',fontproperties=myfont,size=6)
    #plt.xlabel('數量(公噸/年)',fontproperties=myfont,size=6)
    plt.legend(prop=myfont)
    plt.xticks(fontname = 'SimSun',size=10)
    plt.yticks(fontname = 'SimSun',size=10) 
    #plt.savefig('plot.png')
#%%
def test():
    producers_df = load_json('producers.jsonl')
    producers_df = producers_df.drop(['classification', 'canonical_url', 'licenses',
           'first_seen_at', 'last_updated_at', 'followership'],axis=1) #, 'languages'
    #producers_df = producers_df.apply(lambda x: str(x).translate(None, ''.join(['[',']'])) if x.name in ['languages'] else x, axis=1)
    #producers_df = producers_df.apply(lambda x: str(x.value).replace('[',''), axis=1)
    #producers_df = producers_df.replace(regex='1', value='')
    #producers_df.columns
    producers_df.info()
#%%
producers_df = load_json('producers.jsonl')
producers_df = producers_df.drop(['classification', 'canonical_url', 'licenses','languages',
       'first_seen_at', 'last_updated_at', 'followership'],axis=1) 
#producers_df = producers_df.apply(lambda x: str(x).translate(None, ''.join(['[',']'])) if x.name in ['languages'] else x, axis=1)
#test_string.translate(None, ''.join(bad_chars)) 
filenames = find('2020-03-01.jsonl', 'publications') 
archive0_df = load_jsons(filenames)

q_df = archive0_df.drop(['keywords','hashtags','tags','comments','urls'],axis=1) # FIXME: sqlite keyword problem
 
#query_str = """SELECT producer_id,count(producer_id) cnt FROM q_df group by producer_id order by cnt"""
query_str = """
SELECT q.producer_id,count(q.producer_id) cnt,( p.id || "-" || p.name) name FROM q_df q 
inner join
    producers_df p on q.producer_id=p.id
group by q.producer_id order by cnt
"""

qarchive0_df= ps.sqldf(query_str, locals())
plot_test(qarchive0_df,"March article count by producer_id")

