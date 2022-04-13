#跟台灣旅宿網相比，booking.com真的有比較便宜嗎?
#匯入台灣旅宿網計算平均價格
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

conn=sqlite3.connect(r'C:\Users\chuan\TaiwanLegal.sqlite')
cursor=conn.execute('''SELECT *
                    FROM correct_price''')
rows=cursor.fetchall()

L=[]
for row in rows:
    if row[3]!='' and row[4]!='':
        avg_price=(row[3]+row[4])/2
        L.append(avg_price)
    else:
        avg_price=0
        L.append(avg_price)
L1=[]
for row in rows:
    L1.append(row)

columns=["num","city","name","lowest","highest","avg_"]
df=pd.DataFrame(L1,columns=columns)
df=df.drop("avg_",axis=1)
df.insert(5,"avg_p",L)
df.to_sql('correct_price',conn,if_exists='replace',index=False)

num=0
for a in L:
    if a !=0:
        num+=1
print("價格不為空值旅店有",num,"間")
T_total_avg=sum(L)/num
print("台灣旅宿網平均價格為 %.2f 元"%T_total_avg)

conn.close()

#%%
#比較兩者

conn=sqlite3.connect(r'C:\Users\chuan\TaiwanLegal.sqlite')
cursor=conn.execute('''SELECT c.city,c.name,c.lowest,c.avg_p,b.weekday
FROM correct_price AS c
INNER JOIN booking_analysis AS b
ON c.name=b.name;''')
rows=cursor.fetchall()

L=[]
for row in rows:
    L.append(row)
columns=["city","name","t_lowest_p","t_avg_p","b_weekday"]
df=pd.DataFrame(L,columns=columns)

for a in range(len(df)):
    if df.iloc[a,3]==0:
        df=df.drop(df.index[a])

L1=[]
for a in range(len(df)):
    if df.iloc[a,2] !=str(0):
        L1.append(df.iloc[a,2])
L2=[]
for a in L1:
    a=int(a)
    L2.append(a)
    
print("平日Booking平均房價為 %.2f 元"%(sum(df.iloc[:,4])/442))
print("台灣旅宿網平均房價為 %.2f 元"%(sum(df.iloc[:,3])/442))  
print("台灣旅宿網最低平均房價為 %.2f 元"%(sum(L2)/440))
conn.close()
#%%
#迴歸線看與人口關係
conn=sqlite3.connect(r'C:\Users\chuan\TaiwanLegal.sqlite')
cursor=conn.execute('''SELECT city,weekend
FROM booking_analysis''')
rows=cursor.fetchall()

L=[]
for row in rows:
    L.append(row)
columns=["city","weekend_p"]
df=pd.DataFrame(L,columns=columns)

L=[]
a=0
cities=["台中","台北","台南","台東","嘉義","宜蘭","屏東","新北","新竹","桃園","澎湖","花蓮","苗栗","金門","雲林","馬祖","高雄"]
for i in range(len(cities)):
    fliter=(df["city"]==cities[i])
    for i in range(len(fliter)):
        if fliter[i]==True:
            a+=1
    avg=df[fliter].iloc[:,1].sum()/a
    a=0
    L.append(float('%.2f'%avg))

price_data=df.groupby("city").sum()

df2=pd.DataFrame(cities)
df2.insert(1,"p_avg",L)

#人口密度資料匯入
import csv
with open("opendata110N010.csv",encoding="utf-8-sig") as csvFile:
    csvReader=csv.reader(csvFile)
    listReport=list(csvReader)
print(listReport)

listReport.pop(-1) #將不必要資訊移除
listReport.pop(0)

L1=[]
L2=[]
L3=[]
for i in range(len(listReport)):
    a=int(listReport[i][2])
    b=float(listReport[i][3])
    c=int(listReport[i][4])
    L1.append(a)
    L2.append(b)
    L3.append(c)


df1=pd.DataFrame(listReport,columns=["year","zone","pop_n","area","peo_d"])
df1=df1.drop('peo_d',axis=1)
df1=df1.drop('pop_n',axis=1)
df1=df1.drop('area',axis=1)
df1=df1.drop('year',axis=1)
df1.insert(1,"pop_n",L1)
df1.insert(2,"area",L2)
df1.insert(3,"peo_d",L3)

L=[]
for item in range(len(df1)):
    a=df1.iloc[item,3].split('市')
    L.append(a[0])
L1=[]
for item in range(len(L)):
    a=L[item].split('縣')
    L1.append(a[0])
    
#df1=df1.drop("city",axis=1)
df1.insert(4,"city",L1)
#print(df1.groupby('city').sum())
data=df1.groupby('city').sum()

cities=["南投","嘉義","基隆","宜蘭","屏東","彰化","新北","新竹","桃園","澎湖","台中","台北","台南","台東","花蓮","苗栗","連江","金門","雲林","高雄"]
data.insert(3,"cities",cities)
data.to_sql("population",conn,if_exists='replace')

#缺南投、基隆、彰化
data=data.drop("南投",axis=0)
data=data.drop("基隆",axis=0)
data=data.drop("彰化",axis=0)
#把兩個df資訊合併(groupby的sum順序不一樣)
L4=[df2.iloc[4,1],df2.iloc[5,1],df2.iloc[6,1],df2.iloc[7,1],df2.iloc[8,1],df2.iloc[9,1],df2.iloc[10,1],df2.iloc[8,1],df2.iloc[0,1],df2.iloc[1,1],df2.iloc[2,1],df2.iloc[3,1],df2.iloc[11,1],df2.iloc[12,1],df2.iloc[15,1],df2.iloc[13,1],df2.iloc[14,1],df2.iloc[16,1]]

unique = []
for i in L4:         # 1st loop
    if i not in unique:   # 2nd loop
     unique.append(i)

data.insert(4,"price_avg",unique)

#線性回歸
from sklearn.linear_model import LinearRegression

y=pd.DataFrame(np.array(data["price_avg"]),columns=['avg'])
X=pd.DataFrame(np.array(data["pop_n"]/data["area"]),columns=['density'])
lm=LinearRegression()
lm.fit(X,y)
print("迴歸係數:",lm.coef_)
print("截距:",lm.intercept_)

#預測人口密度為5000時的價錢
new_predict=pd.DataFrame(np.array([5000]),columns=['pre_population'])
predict_price=lm.predict(new_predict)
print(predict_price)

#製圖
y=data["price_avg"]
x=data["pop_n"]/data["area"]

plt.rcParams['font.family']='Microsoft YaHei'
plt.rcParams['font.size']=12
plt.figure(dpi=800)

plt.scatter(x,y,c='r')
plt.xlabel("population_density")
plt.ylabel("avg_price")

regression_price=lm.predict(X)
plt.plot(X,regression_price,color='brown')
plt.plot(new_predict,predict_price,marker='o',color='blue',markersize=10)

plt.show()

conn.close()
#%%
#疫情前後「觀光旅館」住房率及營業額差異
#2020資料
import csv
with open("2020_tourhotel.csv",encoding="utf-8-sig") as csvFile:
    csvReader=csv.reader(csvFile)
    listReport=list(csvReader)
#print(listReport)
listReport.pop(-1) #將不必要資訊移除
listReport.pop(0)

#轉為數值型態
L=[]
L1=[]
for i in (range(len(listReport))):
    for item in listReport[i][2:13]:
        data=float(item)
        L.append(data) 
    L1.append(L)
    L=[]
    
df_2020=pd.DataFrame(L1,columns=["stay_num","percentage","avg_price","rent_income","beverage_income","tot_income","room","food","service","others","tot_stuff_sum"])    
L2=["台北地區","台北地區","台北地區","高雄地區","高雄地區","高雄地區","台中地區","台中地區","台中地區","花蓮地區","花蓮地區","桃竹苗地區","桃竹苗地區","桃竹苗地區","風景區","風景區","風景區","其他地區","其他地區","其他地區"]
L3=["國際","一般","小計","國際","一般","小計","國際","一般","小計","國際","小計","國際","一般","小計","國際","一般","小計","國際","一般","小計"]

#插入df
df_2020.insert(11,"city",L2)
df_2020.insert(12,"category",L3)

conn=sqlite3.connect(r'C:\Users\chuan\TaiwanLegal.sqlite')
df_2020.to_sql("df_2020", conn,if_exists='replace',index=True)

conn.close()

#2021資料
import csv
with open("2021_tourhotel.csv",encoding="utf-8-sig") as csvFile:
    csvReader=csv.reader(csvFile)
    listReport=list(csvReader)
listReport.pop(-1) #將不必要資訊移除
listReport.pop(0)

#轉為數值型態
L=[]
L1=[]
for i in (range(len(listReport))):
    for item in listReport[i][2:13]:
        data=float(item)
        L.append(data) 
    L1.append(L)
    L=[]
df=pd.DataFrame(listReport,columns=["city","category","stay_num","percentage","avg_price","rent_income","beverage_income","tot_income","room","food","service","others","tot_stuff_sum"])
df_2021=pd.DataFrame(L1,columns=["stay_num","percentage","avg_price","rent_income","beverage_income","tot_income","room","food","service","others","tot_stuff_sum"])
#分類，讓他跟2020資料相同
L2=["台北地區","台北地區","台北地區","台北地區","台北地區","台北地區","桃竹苗地區","桃竹苗地區","桃竹苗地區","台中地區","台中地區","台中地區","其他地區","其他地區","其他地區","高雄地區","高雄地區","高雄地區","其他地區","其他地區","其他地區","桃竹苗地區","桃竹苗地區","桃竹苗地區","桃竹苗地區","桃竹苗地區","風景區","風景區","其他地區","其他地區","高雄地區","高雄地區","高雄地區","花蓮地區","花蓮地區","花蓮地區","花蓮地區","花蓮地區","風景區","風景區","風景區","台北地區","台北地區","桃竹苗地區","桃竹苗地區","其他地區","其他地區","其他地區","其他地區","其他地區"]
L3=np.array(df.iloc[:,1])

df_2021.insert(11,"city",L2)
df_2021.insert(12,"category",L3)

df_2021.to_sql("df_2021", conn,if_exists='replace',index=True)

conn.close()

#%%兩年對比圖

cursor=conn.execute('''SELECT SUM(stay_num),SUM(rent_income),sum(beverage_income),sum(tot_income),sum(tot_stuff_sum),city,category
FROM df_2021
GROUP BY city,category''')
rows=cursor.fetchall()

L=[]
for row in rows:
    L.append(row)
columns=["sum_staynum","sum_rent_icnome","sum_beverage","tot_income","tot_staff","city","category"]
df=pd.DataFrame(L,columns=columns)

df.to_sql("df_2021_new",conn,if_exists='replace',index=True)

conn.close()

#製作多圖表
import matplotlib.pyplot as plt

cursor=conn.execute('SELECT * FROM df_2021_new')
rows=cursor.fetchall()
L=[]
for row in rows:
    L.append(row)
columns=["index","sum_staynum","sum_rent_icnome","sum_beverage","tot_income","tot_staff","city","category"]
df=pd.DataFrame(L,columns=columns)

cursor2=conn.execute('SELECT * FROM df_2020')
rows=cursor2.fetchall()

L=[]    
L1=[]
for i in range(20):
    L1.append(rows[i][1])
    L1.append(rows[i][4])
    L1.append(rows[i][5])
    L1.append(rows[i][6])
    L1.append(rows[i][11])
    L1.append(rows[i][12])
    L1.append(rows[i][13])
    L.append(L1)
    L1=[]
        
columns=["sum_staynum","sum_rent_icnome","sum_beverage","tot_income","tot_staff","city","category"]
df2=pd.DataFrame(L,columns=columns)

#df-2021,df2-2020
#1 台北/桃竹苗/台中/高雄 (rent_income,berverage_income)
x=np.arange(2)
y1=[[df2.iloc[1,1],df.iloc[6,2]],[df2.iloc[0,1],df.iloc[7,2]],[df2.iloc[1,2],df.iloc[6,3]],[df2.iloc[0,2],df.iloc[7,3]]]
y2=[[df2.iloc[12,1],df.iloc[9,2]],[df2.iloc[11,1],df.iloc[10,2]],[df2.iloc[12,2],df.iloc[9,3]],[df2.iloc[11,2],df.iloc[10,3]]]
y3=[[df2.iloc[7,1],df.iloc[3,2]],[df2.iloc[6,1],df.iloc[4,2]],[df2.iloc[7,2],df.iloc[3,3]],[df2.iloc[6,2],df.iloc[4,3]]]
y4=[[df2.iloc[4,1],df.iloc[18,2]],[df2.iloc[3,1],df.iloc[19,2]],[df2.iloc[4,2],df.iloc[18,3]],[df2.iloc[3,2],df.iloc[19,3]]]
tl=["2020","2021"]

plt.figure(dpi=800)
plt.rcParams['figure.figsize'] = (15,10)
plt.rcParams['font.family']='Microsoft YaHei'
plt.rcParams['font.size']=16
bar_width=0.2

#plot1
plt.subplot(221)
plt.bar(x,y1[0],color='indianred',alpha=0.75,width=bar_width)
plt.bar(x+0.2,y1[1],color='sandybrown',alpha=0.75,width=bar_width)
plt.bar(x+0.4,y1[2],color='lightseagreen',alpha=0.75,width=bar_width)
plt.bar(x+0.6,y1[3],color='skyblue',alpha=0.75,width=bar_width)
plt.xticks(x+1.5*bar_width,tl)
#plt.ylim()
plt.ylabel("Total_income(單位:元)")
plt.title("Taipei")
#plot2
plt.subplot(222)
plt.bar(x,y2[0],color='indianred',alpha=0.75,width=bar_width,label="一般旅館住宿")
plt.bar(x+0.2,y2[1],color='sandybrown',alpha=0.75,width=bar_width,label="國際旅館住宿")
plt.bar(x+0.4,y2[2],color='lightseagreen',alpha=0.75,width=bar_width,label="一般旅館餐飲")
plt.bar(x+0.6,y2[3],color='skyblue',alpha=0.75,width=bar_width,label="國際旅館餐飲")
plt.xticks(x+1.5*bar_width,tl)
plt.ylabel("Total_income(單位:元)")
plt.legend(loc="right", bbox_to_anchor=(1.5,1))
plt.title("Taoyuan")
#plot3
plt.subplot(223)
plt.bar(x,y3[0],color='indianred',alpha=0.75,width=bar_width)
plt.bar(x+0.2,y3[1],color='sandybrown',alpha=0.75,width=bar_width)
plt.bar(x+0.4,y3[2],color='lightseagreen',alpha=0.75,width=bar_width)
plt.bar(x+0.6,y3[3],color='skyblue',alpha=0.75,width=bar_width)
plt.xticks(x+1.5*bar_width,tl)
plt.ylabel("Total_income(單位:元)")
plt.xlabel("Year")
plt.title("Taichung")
#plot4
plt.subplot(224)
plt.bar(x,y4[0],color='indianred',alpha=0.75,width=bar_width)
plt.bar(x+0.2,y4[1],color='sandybrown',alpha=0.75,width=bar_width)
plt.bar(x+0.4,y4[2],color='lightseagreen',alpha=0.75,width=bar_width)
plt.bar(x+0.6,y4[3],color='skyblue',alpha=0.75,width=bar_width)
plt.xticks(x+1.5*bar_width,tl)
plt.ylabel("Total_income(單位:元)")
plt.xlabel("Year")
plt.title("Kaoshiung")

plt.show()


#2 台北/桃竹苗/台中/高雄 (總住用數/員工人數)
x=np.arange(2)
y1=[[df2.iloc[1,0],df.iloc[6,1]],[df2.iloc[0,0],df.iloc[7,1]],[df2.iloc[1,4],df.iloc[6,5]],[df2.iloc[0,4],df.iloc[7,5]]]
y2=[[df2.iloc[12,0],df.iloc[9,1]],[df2.iloc[11,0],df.iloc[10,1]],[df2.iloc[12,4],df.iloc[9,5]],[df2.iloc[11,4],df.iloc[10,5]]]
y3=[[df2.iloc[7,0],df.iloc[3,1]],[df2.iloc[6,0],df.iloc[4,1]],[df2.iloc[7,4],df.iloc[9,5]],[df2.iloc[6,4],df.iloc[10,5]]]
y4=[[df2.iloc[4,0],df.iloc[6,1]],[df2.iloc[3,0],df.iloc[7,1]],[df2.iloc[4,4],df.iloc[6,5]],[df2.iloc[3,4],df.iloc[7,5]]]
tl=["2020","2021"]

plt.figure(dpi=800)
plt.rcParams['figure.figsize'] = (15,10)
plt.rcParams['font.family']='Microsoft YaHei'
plt.rcParams['font.size']=16
bar_width=0.2

#plot1
plt.subplot(221)
plt.bar(x,y1[0],color='indianred',alpha=0.75,width=bar_width)
plt.bar(x+0.2,y1[1],color='sandybrown',alpha=0.75,width=bar_width)
plt.bar(x+0.4,y1[2],color='lightseagreen',alpha=0.75,width=bar_width)
plt.bar(x+0.6,y1[3],color='skyblue',alpha=0.75,width=bar_width)
plt.xticks(x+1.5*bar_width,tl)
#plt.ylim()
plt.ylabel("Total_num(單位:人)")
plt.title("Taipei")
#plot2
plt.subplot(222)
plt.bar(x,y2[0],color='indianred',alpha=0.75,width=bar_width,label="一般旅館住宿數")
plt.bar(x+0.2,y2[1],color='sandybrown',alpha=0.75,width=bar_width,label="國際旅館住宿數")
plt.bar(x+0.4,y2[2],color='lightseagreen',alpha=0.75,width=bar_width,label="一般旅館員工數")
plt.bar(x+0.6,y2[3],color='skyblue',alpha=0.75,width=bar_width,label="國際旅館員工數")
plt.xticks(x+1.5*bar_width,tl)
plt.legend(loc="right", bbox_to_anchor=(1.5,1))
plt.title("Taoyuan")
#plot3
plt.subplot(223)
plt.bar(x,y3[0],color='indianred',alpha=0.75,width=bar_width)
plt.bar(x+0.2,y3[1],color='sandybrown',alpha=0.75,width=bar_width)
plt.bar(x+0.4,y3[2],color='lightseagreen',alpha=0.75,width=bar_width)
plt.bar(x+0.6,y3[3],color='skyblue',alpha=0.75,width=bar_width)
plt.xticks(x+1.5*bar_width,tl)
plt.ylabel("Total_num(單位:人)")
plt.xlabel("Year")
plt.title("Taichung")
#plot4
plt.subplot(224)
plt.bar(x,y4[0],color='indianred',alpha=0.75,width=bar_width)
plt.bar(x+0.2,y4[1],color='sandybrown',alpha=0.75,width=bar_width)
plt.bar(x+0.4,y4[2],color='lightseagreen',alpha=0.75,width=bar_width)
plt.bar(x+0.6,y4[3],color='skyblue',alpha=0.75,width=bar_width)
plt.xticks(x+1.5*bar_width,tl)
plt.xlabel("Year")
plt.title("Kaoshiung")

plt.show()