#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
postgresql related test code, generate rivertree with dot format
Created on Mon Oct 12 06:28:57 2020
@author: wuulong
"""


import psycopg2
from configparser import ConfigParser
#import geopandas
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def config(filename='database.ini', section='postgresql'):
    """ generate db parameters from ini file"""
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

def connect_test():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        # create a cursor
        cur = conn.cursor()
        
	# execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
       
	# close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

def get_sql(sql_str):
    """ query data from sql command """
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(sql_str)
        print("The number of rows: ", cur.rowcount)
        row = cur.fetchone()

        while row is not None:
            print(row)
            row = cur.fetchone()

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def gen_rivertree(filename, rivercode="",id_with_name=False):
    """ 
        load river tree from db:rivercode to networkx graph,df, output dot format
        parameter: 
            filename: filename for dot
            rivercode: rivercode or "" for all
            id_with_name: graph ID with name?
            
        ex: gen_rivertree(dot_filename, "130000")
        return: [G,df]
    
    """

    G = nx.Graph()
    try:
        params = config()
        conn = psycopg2.connect(**params)  
        #print("pass conn")
        sql = "select * from rivercode order by river_id"
        df = pd.read_sql(sql, conn)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    
    lines = []
    dot_strs = {}
    for index, row in df.iterrows():
        link = row['river_link']
        if not rivercode=="":
            if not rivercode in link:
                continue
        #print("processing: %s" %(link))
        cols = link.split("@")
        for i in range(len(cols)-1):
            if cols[i]=='0':
                river_name1 = "海"
                name1 = river_name1
            else:
                river_name1 = df[df['river_id']==cols[i]]['river_name'].values.tolist()
                if len(river_name1)>0:
                    name1 = river_name1[0]
                else:
                    name1 = "Undefined"
            river_name2 = df[df['river_id']==cols[i+1]]['river_name'].values.tolist()
            
            #print("river_name2=%s" %(river_name2[0]))
            if len(river_name2)>0:
                name2 = river_name2[0]
            else:
                name2 = "Undefined"
            dot_str = "\"%s_\\n%s\"->\"%s_\\n%s\"" %(cols[i+1],name2,cols[i],name1)
            #G.add_nodes_from([cols[i], cols[i+1]])
            if id_with_name:
                G.add_node("%s-%s" %(cols[i+1],name2), name=name2)
                G.add_node("%s-%s" %(cols[i],name1), name=name1)
                G.add_edges_from([("%s-%s" %(cols[i+1],name2), "%s-%s" %(cols[i],name1))])
            else:
                G.add_node(cols[i+1], name=name2)
                G.add_node(cols[i], name=name1)
                G.add_edges_from([(cols[i+1], cols[i])])
            if dot_str not in dot_strs:
                dot_strs[dot_str]=1
                #print("dot string: %s" %(dot_str))
                lines.append(dot_str)                     
            
    
    #print("digraph G {\n\t")       
    #lines.sort()
    #print( "\t" + "\n\t".join(lines))
    #print("}\n")     
    
     
    fp = open(filename, "w")
    lines.sort()
    fp.write("%s%s%s" %("digraph G {\n\t\n","\t" + "\n\t".join(lines),"\n}\n"))
    fp.close() 
    return G,df

def output_rivertree(G,rivercode_df):
    if 0:
        print(list(G.nodes))
        print(list(G.edges))
        print(G.nodes['130000'])
    if 1:
        nx.readwrite.gml.write_gml(G,"output/rivertree.gml")
    if 1:
        pos = nx.spring_layout(G)
        colors = range(len(G.edges))
        options = {
            "node_color": "#A0CBE2",
            #"edge_color": colors,
            "width": 1,
            #"edge_cmap": "#A0CBE2",
            "with_labels": True,
        }
        nx.draw(G, pos, **options)
        plt.show()

    #nx.readwrite.nx_shp.write_shp(G, "output/rivertree.shp")
if __name__ == '__main__':
    #connect_test()
    #sql="select * from public.industry_list"
    #sql="select basin_no,basin_name,ST_Area (geom) sqft, area/ST_Area (geom) area_ratio from public.basin"
    #get_sql(sql)
    
    #gen_rivertree("") # 全部
    [G,df]= gen_rivertree("output/rivertree.dot","",False) 
    output_rivertree(G,df)
    