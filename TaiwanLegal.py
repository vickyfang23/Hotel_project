# -*- coding: utf-8 -*-
"""
Created on Sun Jan  9 20:36:29 2022
@author: chuan
"""
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

#取得所有城市名稱
url='https://www.taiwanstay.net.tw/legal-hotel-list?s=t'
header={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62'}
res = requests.get(url,headers=header)
if res.status_code!=200:
    print("連線錯誤!")

soup=BeautifulSoup(res.text,'lxml')
list_city=soup.select("option")
#print(list_city)

city_name=[]
for i in list_city[0:22]:
    city=i.text
    city_name.append(city) 

q=0
#找每一格位置
def find_price():
    url='https://www.taiwanstay.net.tw/legal-hotel-list?hohs_url=&holu_hotel_kind=0%2C1%2C2&search_keyword=&hoci_city='+city_name[q]+'&hoci_area=%E5%85%A8%E9%83%A8&horm_price=&horm_room_num=&horm_room_type=&hohl_evaluation=&hotel_facility_type=&start='+str(count)+'#hotel-list'
    header={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62'}
    res = requests.get(url,headers=header)
    if res.status_code ==200:
        print("連線成功 請稍候...")
    else:
        print("連線失敗")
            
    soup=BeautifulSoup(res.text,'lxml')
    list_a=soup.select('div[class="row bg-color-white margin-bottom-20"]') #select會回傳一個串列
      
    for i in list_a:
        print(i.a.text) #旅社名稱
        print(i.a['href']) #旅社網站連結
        name=i.a.text
    
        hotel_url = i.a['href']
        hotel_res = requests.get(hotel_url,headers=header)
        hotel_soup = BeautifulSoup(hotel_res.text,'html.parser')
        hotel_table = hotel_soup.select('div[class="parallax-counter-v2 margin-bottom-60"] table[class="table table-striped"]')
        #print(hotel_table[0].caption.text)
        
        
        price_set={}
        try:
           hotel_td = hotel_table[0].select('td')
           print(hotel_td[1].text) #旅社價錢
           print("\n")
           price=hotel_td[1].text        
           #存入字典
           price_set["city"]=city_name[q]
           price_set["name"]=name
           price_set["price"]=price
           
           #存入列
           L.append(price_set)
           # #存入json檔
           # filename="TaiwanLegal.json"
           # with open (filename,'a',encoding='utf-8-sig') as jsonfile:
           #     json.dump(price_set,jsonfile,ensure_ascii=False)
        except:
            print("查無價錢")
            price='non'
            price_set["city"]=city_name[q]
            price_set["name"]=name
            price_set["price"]=price
            L.append(price_set)
            # filename="TaiwanLegal.json"
            # with open (filename,'a',encoding='utf-8-sig') as jsonfile:
            #     json.dump(price_set,jsonfile,ensure_ascii=False)
L=[]  
for i in city_name:
    count=0  
    url='https://www.taiwanstay.net.tw/legal-hotel-list?hohs_url=&holu_hotel_kind=0%2C1%2C2&search_keyword=&hoci_city='+i+'&hoci_area=%E5%85%A8%E9%83%A8&horm_price=&horm_room_num=&horm_room_type=&hohl_evaluation=&hotel_facility_type=&start='+str(count)+'#hotel-list'
    header={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62'}
    res = requests.get(url,headers=header)
    if res.status_code ==200:
        print("連線成功 請稍候...")
    else:
        print("連線失敗")
        
    soup=BeautifulSoup(res.text,'lxml')
    #print(soup.prettify) 看結構
    
    #算這個縣市共有幾頁
    num=soup.select('div[class="text-center all_num"]')
    num_span=num[0].select('span')
    print("共",num_span[0].text,"頁")
    num=int(num_span[0].text)
  
    #呼叫方法
    j=-1
    while j<num:
        count=(j+1)*25
        find_price()
        j+=1
        if j==num:
            q+=1
            break 
                        
#讀取json檔，整理後存進資料庫
file=open('TaiwanLegal.json','w',encoding='utf-8-sig')
data=json.dump(L,file,ensure_ascii=False)
file.close()

file=open('TaiwanLegal.json','r',encoding='utf-8-sig')
data=json.load(file)
write_to_sql=[]
for item in data:
    d=[item['city'],item['name'],item['price']]
    write_to_sql.append(d)
    
#存成dataframe    
df=pd.DataFrame(write_to_sql,columns=['city','name','price'])
#存入資料庫
import sqlite3
conn=sqlite3.connect(r'C:\Users\chuan\TaiwanLegal.sqlite')
df.to_sql('price', conn,if_exists='replace',index=True)

conn.close()

#ods檔(含有所有基本資訊的)轉存入資料庫
import csv
with open('document.csv','r',encoding='utf-8-sig')as file:
    csvReader=csv.reader(file)
    listReader=list(csvReader)

print(listReader)

L=['no','type','name','city','conty','code','addr','tel','roomnum','website']
df1=pd.DataFrame(listReader[1:13633],columns=L)

conn=sqlite3.connect(r'C:\Users\chuan\TaiwanLegal.sqlite')
df1.to_sql('data',conn,if_exists='replace',index=True)

conn.close()

#讀取資料庫資料，並分割價錢欄位(資料清理)
conn=sqlite3.connect(r'C:\Users\chuan\TaiwanLegal.sqlite')
print("connect successfully")

cursor=conn.execute('SELECT * FROM price')
print(cursor)

rows=cursor.fetchall()
print(rows)

L=[]
for row in rows:
    a=list(row)
    L.append(a)

df=pd.DataFrame(L,columns=['no','city','name','price'])
print(df.iloc[:,3])

L=[]
for item in df.iloc[:,3]:
    try:
        a=item.split('NT$')
        L.append(a)
    except:
        L.append(item)
        
lowest_price=[]
highest_price=[]    
for item in L:
    try:
        b=item[1].split('-')
        lowest_price.append(int(b[0]))
        highest_price.append(int(b[1]))
    except:
        lowest_price.append('')
        highest_price.append('')

#新增欄位(最低價&最高價)存入資料庫
df.insert(4,column="lowest",value=lowest_price)
df.insert(5,column="hightest",value=highest_price)

df.to_sql('correct_price', conn,if_exists='replace',index=True)

conn.commit()
conn.close()

#%% 資料分析


