#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
README: 轉換格式 從 臺灣生物分類階層樹狀名錄
Input: https://taibnet.sinica.edu.tw/AjaxTree/allkingdom.php?
id detail: #https://taibnet.sinica.edu.tw/chi/taibnet_species_detail.php?name_code=201102&tree=y
API by hack: https://taibnet.sinica.edu.tw/AjaxTree/xml.php?id=%s
CSV 格式：
    id,level,link,child,pid,name,ename,memo,text
    項目 ID, 第幾層 ,從頭到此的結構 ,是否有子項（0:屬 1:非屬）,上層代號,中文名稱,英文名稱,備註（此項資料下面有多少項目）,項目原始 text
@author: wuulong
"""

#%% get XML
import os
import requests

import pandas as pd 
import xml.etree.ElementTree as etree
import re

load_cnt = 0 # 讀取的項目數量， debug purpose
#%% 資料儲存
class BioTree():
    def __init__(self,root_id,root_level,root_link):
        self.root ={} # [level,link,result] ,
        self.root_id = root_id #植物界
        self.root_level = root_level #界:1
        self.root_link = root_link # 7-x-x
        
#%% 下載 xml, 如果已經下載過，會跳過
def url_to_file(url,pathname,reload=False):
    #print("url_to_file: url=%s, pathname=%s" %(url,pathname))
    global load_cnt
    
    need_load= True
    if reload==False and os.path.isfile(pathname) :
        need_load = False
    if need_load:
        try:
            r = requests.get(url, allow_redirects=True,verify=False)
            open(pathname, 'wb').write(r.content)
        except:
            return False
    load_cnt += 1
    if load_cnt % 100 ==0 :
        print("loading cnt = %i" %(load_cnt))
    return True


#%% 將 XML 轉換成 list

def parse_xml(filename):
    try:
        tree = etree.parse(filename)
        root = tree.getroot()
    
    
        dataname = root[0].tag #FIME: need more check no data
        result = []
        for item in root.findall(dataname):
            id = item.attrib['id']
            child = item.attrib['child']
            text = item.attrib['text']
            #m = re.search('(\S+)\s+(.*)<font.*>(.*)</font>',text)
            #print("child=%s,id=%s,name=%s,ename=%s,memo=%s,text=%s" %(child,id,m.group(1),m.group(2),m.group(3).strip(),text))
            result.append([id,child,text])
    except:
        result = None
    return result #[ [id,child,text],[id,child,text],... ]
#%% 取得與處理某個 id
def get_id(id):
    url="https://taibnet.sinica.edu.tw/AjaxTree/xml.php?id=%s" %(id) 
    status = url_to_file(url,"%s.xml" %(id),False)
    if not status:
        print("!!! Get URL exception: id=%i" %(id))
        return None
    
    filename = "%s.xml" %(id)
    result = parse_xml(filename)
    if result is None:
        print("!!! Parse XML Exception: id=%s " %(id))
    return result

#%% 將 item 中的 text, 取出名稱，英文學名， memo
def parse_text(id,child,text):
    if child=='1':
        m = re.search('(\S+)\s+(.*)<font.*>(.*)</font>',text)
        name = m.group(1)
        ename = m.group(2).replace('<i>','').replace('</i>','')
        memo = m.group(3).strip()
        #print("child=%s,id=%s,name=%s,ename=%s,memo=%s,text=%s" %(child,id,name,ename,memo,text))
    else:
        if text[0]=='<':
            m = re.search('(.*)<font.*>(.*)</font>',text)
            name = ""
            ename_str = m.group(1)
        else:
            m = re.search('(\S*)\s*(.*)<font.*>(.*)</font>',text)
            name = m.group(1)
            ename_str = m.group(2)
        m2 = re.findall("<i>(.*?)</i>", ename_str, flags=0)
        ename = " ".join(m2)
        memo = ""
        #print("child=%s,id=%s,name=%s,ename=%s, text=%s" %(child,id,name,ename, text))
    return [id, child, name, ename, memo]
    
#%% 遞迴取id
def travel_id(oid,level,link, root, recurisve=False):
    result = get_id(oid)
    if result is None:
        return 
    root[oid]=[level,link,result]
    
    for [id,child,text] in result:
        if child=='1':
            if recurisve:
                if link:
                    link_str = "%s-%s" %(link,id)
                else:
                    link_str = id
                travel_id(id, level+1, link_str,root, True)    
#%% 將結果輸出到螢幕或是檔案（CSV）
def dump_root(root,filename):
    if filename != "":
        # 開啟檔案
        fp = open(filename, "w",encoding='UTF-8')
        fp.write("id,level,link,child,pid,name,ename,memo,text\n")

    for pid in root.keys():
        result = root[pid][2]
        level = root[pid][0]+1
        link =  root[pid][1]
        for [id,child,text] in result:
            [id, child, name, ename, memo] = parse_text(id,child,text)
            if link:
                link_str = "%s-%s" %(link,id)
            else:
                link_str = id
            if filename != "":
                fp.write("%s,%i,%s,%s,%s,%s,%s,%s,%s\n" %(id,level,link_str, child,pid,name,ename, memo, text))
            else:
                print("id=%s,level=%i,link=%s,child=%s,pid=%s,name=%s,ename=%s, memo=%s, text=%s" %(id,level,link_str,child,pid,name,ename, memo, text))

    if filename != "":
        fp.close()
#%% 設定/取得/輸出
#oid='71004010012'
bt = BioTree('0',0,"") #此例為全部
#bt = BioTree('1',3,"1-0-0") #處理的ID, 第幾層（界為第一層），從上到此層的結構（如維管束植物門為 7-710） ，此例為植物界
#bt = BioTree('7',1,"7) #處理的ID, 第幾層（界為第一層），從上到此層的結構（如維管束植物門為 7-710） ，此例為植物界
travel_id(bt.root_id,bt.root_level,bt.root_link,bt.root, True)
dump_root(bt.root,"biotree.csv")
