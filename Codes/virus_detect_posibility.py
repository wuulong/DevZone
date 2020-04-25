#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 07:37:45 2020
染病正確率計算,有病率估計
參考： https://www.facebook.com/permalink.php?story_fbid=2965126610218341&id=100001630939939
@author: wuulong
"""
#sick_rate = 0.014 # 有病率
#detect_rate = 0.99 # 準確率

sick_tbl = [0.0001,0.001,0.014,0.1]
detect_tbl = [0.3,0.5,0.7,0.9,0.95,0.99,0.999]

def posbility_cal(sick_rate, detect_rate):
    total_cnt = 10000
    
    sick_cnt = total_cnt * sick_rate
    nosick_cnt = total_cnt * (1-sick_rate)
    
    sick_pos_cnt = sick_cnt * detect_rate
    sick_na_cnt = sick_cnt * (1-detect_rate )
    nosick_pos_cnt = nosick_cnt * (1-detect_rate )
    nosick_na_cnt = nosick_cnt * detect_rate
    
    p_sick_pos = float(sick_pos_cnt) / (sick_pos_cnt + nosick_pos_cnt)
    return p_sick_pos

def est_sick_rate(detect_rate, quality_rate):
    test_range = [0,1]
    p_sick_pos = 1.0
    cur_rate = 0.5
    p_sick_pos = 1.0
    pass_rate = 1.0
    while 1:
        if abs(p_sick_pos - quality_rate) < 0.001:
            return [cur_rate,pass_rate]
            
        cur_rate = float(test_range[0] + test_range[1])/2
        p_sick_pos = posbility_cal(cur_rate,detect_rate)
        #print("%f,%f" %(cur_rate,p_sick_pos))
        if p_sick_pos >= quality_rate:
            pass_rate = p_sick_pos
            test_range[1]=cur_rate
        else:
            test_range[0]=cur_rate

print("---- 染病正確率 (檢驗出染病並且真的染病的機率 )  -----")
print("有病率\t", end = '')
for detect_rate in detect_tbl:
    print( "%02.1f%%\t" %(detect_rate*100), end = '')
print("<-- 檢驗準確率")

for sick_rate in sick_tbl:
    print( "%02.2f%%\t" %(sick_rate*100), end = '')
    for detect_rate in detect_tbl:
        p = posbility_cal(sick_rate,detect_rate)
        print( "%02.2f%%\t" %(p*100), end = '')
    print('')
print("舉例說明:運用檢驗率工具 %02.1f%%, 在有病率為%02.2f%% 情況下，染病正確率為%02.2f%%" %(detect_rate*100,sick_rate*100,p*100))
    
quality_tbl = [0.0001,0.001,0.01,0.05, 0.1,0.2,0.3,0.5,0.7,0.9,0.95,0.99,0.999]
detect_tbl = [0.3,0.5,0.7,0.9,0.95,0.99,0.999]
    
print("\n\n---- 有病率(在染病正確率的要求下，只有這種準確率的工具，需要有病率高於此值才能達到要求)   -----")
print("染病正確率\t", end = '')
for detect_rate in detect_tbl:
    print( "%02.1f%%\t" %(detect_rate*100), end = '')
print("<-- 檢驗準確率")

for quality_rate in quality_tbl:
    print( "%02.2f%%\t" %(quality_rate*100), end = '')
    for detect_rate in detect_tbl:
        [cur_rate,pass_rate] = est_sick_rate(detect_rate,quality_rate)
        print( "%02.2f%%\t" %(cur_rate*100), end = '')
    print('')
print("舉例說明：運用檢驗率工具 %02.1f%%, 在染病正確率要求為%02.2f%% 情況下，有病率需高於%02.2f%% 才能達到要求"%(detect_rate*100,quality_rate*100,cur_rate*100))

#detect_rate = 0.99
#quality_rate = 0.58
#[cur_rate,pass_rate] = est_sick_rate(detect_rate,quality_rate)
#print("準確率=%.1f%%,要求染病正確率=%.1f%%,有病率=%.2f%%,染病正確率=%.2f%%" %(detect_rate*100,quality_rate*100,cur_rate*100,pass_rate*100))
