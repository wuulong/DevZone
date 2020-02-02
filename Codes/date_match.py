# 完全對稱日, 所謂完全對稱日，就是指把西元日期以YYYY-MM-DD型式寫出時，由左至右或由右至左都一樣的日期，2020年2月2日的20200202就是一例
from datetime import datetime,timedelta

fmt = '%Y-%m-%d'
dt = datetime.strptime("1000-01-01", fmt)
dt_end = datetime.strptime("9999-12-31", fmt)
i = 1
while True:
    txt_dt = dt.strftime('%Y%m%d')
    rev_dt = txt_dt[::-1]
    #print(txt_dt)
    if txt_dt == rev_dt:
        print("MATCH! - %s - pos: %i" %(txt_dt,i)) 
        i += 1
    if dt == dt_end:
        break
    dt +=  timedelta(days=1)

