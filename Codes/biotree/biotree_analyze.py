#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
README: analyze iNaturalist export data
. plot biotree from iNaturalist export data
. plot cluster diagram : dendrogram
@author: wuulong
"""
#%%
import pandas as pd
#import pandasql as ps
from graphviz import Digraph
import numpy as np

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
        enames_u = self.nat_df.scientific_name.unique()
        enames = enames_u.tolist()
        enames.remove(np.nan)
        #enames = enames[~np.isnan(enames)]
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
        #print("dump dot enames=%s" %("\n".join(enames)))
         
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
        print("dotnode unique=%s" %(dotnode_unique))
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
    
    def ename_to_field(self,ename,fieldname):
        link_s = self.bt_df[self.bt_df['ename']==ename][fieldname]
        links = link_s.values.tolist()
        if len(links)>=1:
            #print("ename=%s found link" %(ename))
            return links[0]
        print("ename=%s can't find %s" %(ename,fieldname))
        return None
    def link_to_distvalue(self,a,b):
        cols_a = a.split("-")
        cols_b = b.split("-")
        v = 0
        len_min = min(len(cols_a),len(cols_b))
        for i in range(len_min):
            if cols_a[i] != cols_b[i]:
                #v += 2**(6-i)
                return 7-i
        return 0
        
        
    def gen_bio_dismax(self,enames_need):
        
        enames = []
        for ename in enames_need:
            link = ba.ename_to_field(ename,'link')
            if link is not None:    
                enames.append(ename)
        
        #print(enames)
        
        #print(enames)
        #a=ba.ename_to_link('Capsicum annuum')
        #b=ba.ename_to_link('Carica papaya')
        
        
        dist_matrix = []
        for i in range(len(enames)):
            for j in range(i+1,len(enames)):
                if i!=j:
                    a = ba.ename_to_field(enames[i],'link')
                    b = ba.ename_to_field(enames[j],'link')
                    
                    
                    v = ba.link_to_distvalue(a,b)
                    dist_matrix.append(v)
                    #print("%s=%s\t%s=%s,v=%i" %(enames[i],a,enames[j],b,v))
        return [enames,dist_matrix]
#%%
def gen_diagram(A, disMat):
    import scipy
    import scipy.cluster.hierarchy as sch
    from scipy.cluster.vq import vq,kmeans,whiten
    import matplotlib.pylab as plt
    from matplotlib.font_manager import FontProperties
    
    
    myfont = FontProperties(fname=r'/Library/Fonts/Microsoft/SimSun.ttf')

    #myfont = FontProperties(fname=r'/Library/Fonts/Microsoft/MingLiU.ttf')
    plt.rcParams["font.family"] = "SimSun"
    fig = plt.gcf()
    fig.set_size_inches(18.5, 20)
    #fig.set_size_inches(30, 20)
    
    ax = plt.gca()
    
    ax.tick_params(axis='x', which='both', labelsize=20,size=20,colors='b')
    ax.tick_params(axis='y', which='both', labelsize=20,size=20)

    #進行層次聚類:
    Z=sch.linkage(disMat,method='single') 
    #將層級聚類結果以樹狀圖表示出來並儲存為plot_dendrogram.png
    P=sch.dendrogram(Z,labels=A)
    
    plt.savefig('dendrogram.pdf')

#%%
ba = BioAna()
ba.load_biotree("biotree.csv")
ba.load_inat("inat_export.csv")
#enames_need = ['Chamaesyce maculata','Woodwardia japonica','Basella alba']
enames_need = ba.nat_get_enames()

if 1: # gen dot
    ba.dump_dot_by_ename(enames_need)

if 1: #gen cluster diagram
    [enames, dist_matrix] = ba.gen_bio_dismax(enames_need)
    
    # prepare label with chinese name
    names = []
    for ename in enames:
        name = ba.ename_to_field(ename,'name')
        if name is not None:    
            names.append("%s\n%s" %(name,ename))
        else:
            names.append("%s" %(ename))        
    print("names=%s\ndist_matrix=%s" %(names,dist_matrix))
    
    gen_diagram(names,dist_matrix)

