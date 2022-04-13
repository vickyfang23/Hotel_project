from bs4 import BeautifulSoup
from selenium import webdriver
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import json
import pandas as pd

#設定想要查詢的城市
city_name=['基隆','台北','新北','桃園','新竹','苗栗','台中','雲林','嘉義','台南','高雄','屏東','台東','花蓮','宜蘭','金門','馬祖','澎湖']

#點選城市、日期
for j in range(18):
    driver=webdriver.Chrome(ChromeDriverManager().install())
    driver.implicitly_wait(5)
    driver.get('https://www.booking.com/index.zh-tw.html')
    time.sleep(2)
    driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/form/div[1]/div[1]/div[1]/div[1]/label/input').send_keys(city_name[j])
    driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/form/div[1]/div[2]/div[1]/div[2]/div/div/div/div/span').click()
    content=driver.find_elements_by_tag_name('td')
    content[38].click()
    content[39].click()
    
    driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/form/div[1]/div[4]/div[2]/button').click()
    time.sleep(2)
    #印出共有幾間旅店
    title=driver.find_element_by_tag_name('h1')
    print(title.text)

    page_remaining=True
    
    L=[]
    while page_remaining:   
    #蒐集旅店名稱/鄉鎮地點/價錢等資訊
        for i in range(25):
            try:
                Dict={}
                soup=BeautifulSoup(driver.page_source,'lxml')
                name=soup.find_all('div',{"class":"fde444d7ef _c445487e2"})
                conty=soup.find_all('span',{"class":"af1ddfc958 eba89149fb"})
                price=soup.find_all('span',{"class":"fde444d7ef _e885fdc12"})
                print(name[i].get_text())
                print(conty[2*(i-1)+2].get_text())
                print(price[i].get_text())
                Dict["city"]=city_name[j]
                Dict["name"]=name[i].get_text()
                Dict["conty"]=conty[2*(i-1)+2].get_text()
                Dict["price"]=price[i].get_text()
                L.append(Dict)
            except:
                print("out of list")
                page_remaining=False
                break
        if page_remaining==True:
            try:
                next_link=driver.find_element_by_xpath('/html/body/div[2]/div/div[4]/div[1]/div[1]/div[4]/div[3]/div/div/div/div/div[7]/div[2]/nav/div/div[3]/button')
                next_link.click()
                time.sleep(5)
            except NoSuchElementException:
                print("element_not_exist")
                file=open('booking_com_normal.json','a',encoding='utf-8-sig')
                data=json.dump(L,file,ensure_ascii=False)
                file.close()
                break
            except:
                next_link=driver.find_element_by_xpath('/html/body/div[2]/div/div[4]/div[1]/div[1]/div[5]/div[3]/div/div/div/div/div[7]/div[2]/nav/div/div[3]/button')
                next_link.click()
                time.sleep(5)
        else:
            #存進json檔
            file=open('booking_com_normal.json','a',encoding='utf-8-sig')
            data=json.dump(L,file,ensure_ascii=False)
            file.close()
            break   
driver.close()


file=open('booking_com.json','r',encoding='utf-8-sig')
data=json.load(file)
write_to_sql=[]
for item in data:
    d=[item['city'],item['conty'],item['name'],item['price']]
    write_to_sql.append(d)

df=pd.DataFrame(write_to_sql,columns=['city','conty','name','price'])

#移除重複項
df1=df.drop_duplicates(subset=None, 
                          keep='first', 
                          inplace=False, 
                          ignore_index=False)
#刪除價錢字符
L=[]
for item in df1.iloc[:,3]:
    a=item.split('TWD')
    L.append(a)

price=[]
for item in L:
    b=item[1].split( )
    price.append(b[0])

L=[]
for item in price:
    try:
        c=item.replace(",","")
        L.append(int(c))
    except:
        L.append(int(item))
        pass

#存進資料庫
del df1['price']    
df1.insert(3,column="price",value=L)
import sqlite3
conn=sqlite3.connect(r'C:\Users\chuan\TaiwanLegal.sqlite')
df1.to_sql('booking_com_weekday', conn,if_exists='replace',index=True)

conn.close()