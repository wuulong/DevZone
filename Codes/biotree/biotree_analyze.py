#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
README: analyze iNaturalist export data
. plot biotree from iNaturalist export data
@author: wuulong
"""
#%%
import pandas as pd
#import pandasql as ps
from graphviz import Digraph
#%% 
class BioAna():
    def __init__(self):
        self.bt_df = None
    def load_biotree(self,filename):
        #self.bt_df = pd.read_csv(filename,delimiter='|')
        self.bt_df = pd.read_csv(filename)
    def load_inat(self,filename):
        self.nat_df = pd.read_csv(filename)
    # get unique scientific_name name from iNat
    def nat_get_enames(self):
        enames = self.nat_df.scientific_name.unique() 
        return enames
    # find unique ids by level 
    def links_unique_level(self,links,level):
        ids = {}
        for link in links:
            cols = link.split('-')
            if len(cols)>= level:
                v = cols[level-1]
                ids[v] = 1
        return ids.keys()
    #            
    def dump_dot_by_ename(self,enames): #[ename,ename,...]
        # get link by enames
        link_s = self.bt_df[self.bt_df['ename'].isin(enames)]['link']
        links = link_s.values.tolist()
        print(links)
        
        # get unique nodes, links
        dotlink_unique = {}
        dotnode_unique = {}
        for link in links:
            cols = link.split('-')
            for i in range(1,len(cols)):
                key = "%s-%s" %(cols[i-1],cols[i])
                dotlink_unique[key]=1
                dotnode_unique[cols[i-1]]=1
                dotnode_unique[cols[i]]=1
        
        # plan dot
        dot = Digraph(comment='BioTree Analyze')
        for key in dotnode_unique.keys():
            cols = key.split('-')
            name = self.bt_df[self.bt_df['id']==cols[0]]['name'].values.tolist()
            ename = self.bt_df[self.bt_df['id']==cols[0]]['ename'].values.tolist()
            dot.node(key,"%s\n%s" %(name[0],ename[0]))            
        
        for key in dotlink_unique.keys():
            cols = key.split('-')
            dot.edge(cols[0], cols[1])
        
        #dot output
        print(dot.source)  # doctest: +NORMALIZE_WHITESPACE
        dot.render('test-output/inat_tree_plot', view=True)
        
        # backup
        if 0:
            for key in dotlink_unique.keys():
                cols = key.split('-')
                s_name = self.bt_df[self.bt_df['id']==cols[0]]['name'].values.tolist()
                s_ename = self.bt_df[self.bt_df['id']==cols[0]]['ename'].values.tolist()
                d_name = self.bt_df[self.bt_df['id']==cols[1]]['name'].values.tolist()
                d_ename = self.bt_df[self.bt_df['id']==cols[1]]['ename'].values.tolist()
                print("%s %s->%s %s" %(s_name[0],s_ename[0],d_name[0],d_ename[0]))
        
                
            
        

#%%
ba = BioAna()
ba.load_biotree("biotree.csv")
ba.load_inat("inat_export.csv")
enames = ba.nat_get_enames()
#enames = ['Capsicum annuum','Carica papaya','Basella alba']
ba.dump_dot_by_ename(enames)


