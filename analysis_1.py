#分析資料
#Booking.com在平日/假日/連續假期的價差?
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
conn=sqlite3.connect(r'C:\Users\chuan\TaiwanLegal.sqlite')

cursor=conn.execute('''SELECT DISTINCT bw.city,bw.conty,bw.name,bw.price AS weekday,bn.price AS normal,bv.price AS vacation 
FROM (booking_com_weekday AS bw
INNER JOIN booking_com_normal AS bn
ON bw.name = bn.name AND bw.city=bn.city)
INNER JOIN booking_com_vacation AS bv
using (name,city);''')

rows=cursor.fetchall()

L=[]
for row in rows:
    a=list(row)
    L.append(a)

columns=["city","conty","name","weekend","weekday","holiday"]
df=pd.DataFrame(L,columns=columns)

weekend_sum=df.iloc[:,3].sum()
weekday_sum=df.iloc[:,4].sum()
holiday_sum=df.iloc[:,5].sum()

weekend_avg=float('%.2f'%(weekend_sum/len(df)))
weekday_avg=float('%.2f'%(weekday_sum/len(df)))
holiday_avg=float('%.2f'%(holiday_sum/len(df)))

print("符合條件共",len(df),"間房源")
print("假日平均房價為:",weekend_avg,"元")
print("平日平均房價為:",weekday_avg,"元")
print("特殊假期平均房價為:",holiday_avg,"元")

#%%分地區
city=["台北","新北","桃園","台中","台南","高雄","花蓮","台東"]

def place():
    import pandas as pd
    import sqlite3
    conn=sqlite3.connect(r'C:\Users\chuan\TaiwanLegal.sqlite')
    
    test='''SELECT DISTINCT bw.city,bw.conty,bw.name,bw.price AS weekday,bn.price AS normal,bv.price AS vacation 
    FROM (booking_com_weekday AS bw
    INNER JOIN booking_com_normal AS bn
    ON bw.name = bn.name)
    INNER JOIN booking_com_vacation AS bv
    using (name)
    WHERE bw.city =\''''  + city[i]  +"\'"
    
    cursor=conn.execute(test)

    rows=cursor.fetchall()
    print(rows)

    L=[]
    for row in rows:
        a=list(row)
        L.append(a)

    columns=["city","conty","name","weekend","weekday","holiday"]
    df=pd.DataFrame(L,columns=columns)
    
    weekend_sum=df.iloc[:,3].sum()
    weekday_sum=df.iloc[:,4].sum()
    holiday_sum=df.iloc[:,5].sum()
    weekend_avg=float('%.2f'%(weekend_sum/len(df)))
    weekday_avg=float('%.2f'%(weekday_sum/len(df)))
    holiday_avg=float('%.2f'%(holiday_sum/len(df)))
    return weekend_avg,weekday_avg,holiday_avg

compare=[]
for i in range(8):
    a=place()
    compare.append(list(a))

columns=["weekend","weekday","holiday"]
df=pd.DataFrame(compare,columns=columns)

#繪圖
plt.rcParams['font.family']='Microsoft YaHei'
plt.rcParams['font.size']=12

plt.figure(dpi=800)

city=city[0:6]
weekend=df.iloc[0:6,0]
weekday=df.iloc[0:6,1]
holiday=df.iloc[0:6,2]

x = np.arange(len(city))
width=0.3

plt.bar(x,weekend,width,color='#ffc284',label='weekend')
plt.bar(x+width,weekday,width,color='#00a1bc',label='weekday')
plt.bar(x+width*2,holiday,width,color='#cf4969',label='holiday')
plt.xticks(x + width, city)
plt.ylabel("Avg Price")
plt.title("Hotels Avg Price in Municipality")

for a,b in zip(x,holiday):
    if a==3 or a==4:
        plt.text(a+0.6, b+0.05, '%.2f' % b, ha='center', va= 'bottom',fontsize=10)
    else:
        pass
plt.legend(bbox_to_anchor=(1,1), loc='upper left')
plt.show()
#%%多一欄做每列的相減
#假期/假日減平日
L=[]
for item in range(len(df)):
    spread=df.iloc[item,5]-df.iloc[item,4]
    L.append(spread)
L1=[]
for item in range(len(df)):
    spread=df.iloc[item,3]-df.iloc[item,4]
    L1.append(spread)
print("假期與平日,平均價差為%.2f元"%(sum(L)/1246))
print("假日與平日,平均價差為%.2f元"%(sum(L1)/1246))

df.insert(6,"holiday_spread",L)
df.insert(7,"weekend_spread",L1)

#各選出溢價最高旅店降冪排序
df_spread=df.sort_values(by=["holiday_spread"],ascending=False)
df_spread2=df.sort_values(by=["weekend_spread"],ascending=False)
print("假期價差最高的旅館為:",df_spread.iloc[0,0],df_spread.iloc[0,2],",",df_spread.iloc[0,6],"元")
print("假日價差最高的旅館為:",df_spread2.iloc[0,0],df_spread2.iloc[0,2],",",df_spread.iloc[0,7],"元")

df.to_sql('booking_analysis', conn,if_exists='replace',index=True)

conn.close()