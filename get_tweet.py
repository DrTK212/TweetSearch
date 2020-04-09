# -*- coding: utf-8 -*-
"""
Created on Sun Oct 21 21:02:12 2018

@author: Ryutaro Takanami
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import csv
import sys
sys.path.append('/anaconda/lib/python3.5/site-packages')
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import time
import pandas as pd
import openpyxl


TWEET_NUM = 1



url = "https://twitter.com/search?f=tweets&vertical=default&q=%E3%83%AF%E3%83%B3%E3%82%B0%E3%83%BC%E3%83%95%E3%82%A7%E3%82%B9&src=typd&lang=ja"

path_to_chromedriver = 'C:/Users//ディレクトリ指定/chromedriver'
browser = webdriver.Chrome(executable_path = path_to_chromedriver)

browser.get(url);


scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('WONGOO FES analysis-ebe8394b808c.json', scope)
gc = gspread.authorize(credentials)
wks = gc.open('wongoo-fes').sheet1


file_out = 'C:/Users/Ryutaro Takanami/.spyder-py3/WONGOO_FES/tweet.csv'
tweet_list = []


def twt_scroller(url):

    browser.get(url)
    
    #define initial page height for 'while' loop
    lastHeight = browser.execute_script("return document.body.scrollHeight")
    
    for a in range(100):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        #define how many seconds to wait while dynamic page content loads
        time.sleep(2)
        newHeight = browser.execute_script("return document.body.scrollHeight")
        
        if newHeight == lastHeight:
            break
        else:
            lastHeight = newHeight
            
    html = browser.page_source

    return html



def blogxtract(url):
    

    count = 0
    #set to global in case you want to play around with the HTML later   
    global soup    
    
    #call dynamic page scroll function here
    soup = BeautifulSoup(twt_scroller(url), "html.parser")
    #ページスクロースをしないでデータを収集する
    #soup = BeautifulSoup(browser.page_source, "html.parser")
    
    #一定のツイート数を取得したい場合に一連のtweet_numをアクティブに
    #tweet_num = TWEET_NUM
    
    for i in soup.find_all('li', {"data-item-type":"tweet"}):
        
                
        try:
            #tweet_num -= 1
            count +=1
            print(count)
            date = (i.small.a['title'] if i.small is not None else "")
            pattern = "(.*) - (.*)"
            d = re.search(pattern, date)
            
            tim = d.group(1)
            day = d.group(2)
            
            t = int(re.search("(.*):", tim).group(1)) + 16
            if (t >= 24):
                t -=24
                tim = re.sub("(.*):", str(t) + ":" , tim)
                
                pattern = u'[月]'"(.*)"u'[日]'
                d = int(re.search(pattern, date).group(1)) + 1
                day = re.sub(u'[月]'"(.*)"u'[日]', u'月'+ str(d) + u'日', day)
            
            else:
                tim = re.sub("(.*):", str(t) + ":" , tim)
                
            
            user_name = (i.div['data-name'] if i.div is not None else "")
            user_id = (i.div['data-screen-name'] if i.div is not None else "")
            text = (i.find('p', class_ = 'TweetTextSize').get_text() if i.p is not None else "")
            
            #テキストに指定の単語が入っていないツイートは取得しないようにする（twitterの単語指定だとユーザ名に検索ワードが入っていると取得してしまうため）
            if(text.find("検索ワード")==-1):
                continue
            
            rep = i.find('div', class_ = 'ProfileTweet-action ProfileTweet-action--reply').find("span",{"class":"ProfileTweet-actionCountForPresentation"}).get_text()
            if (rep == ""):
                rep = 0
            
            
            ret = i.find('div', class_ = 'ProfileTweet-action ProfileTweet-action--retweet js-toggleState js-toggleRt').find("span",{"class":"ProfileTweet-actionCountForPresentation"}).get_text()
            if (ret == ""):
                ret = 0
            
            
            fav = i.find('div', class_ = 'ProfileTweet-action ProfileTweet-action--favorite js-toggleState').find("span",{"class":"ProfileTweet-actionCountForPresentation"}).get_text()
            if (fav == ""):
                fav = 0
            
            
            
            tweet_dict = {
                "day": str(day), 
                "tim": str(tim), 
                "user_name": str(user_name), 
                "user_id": str(user_id), 
                "text": str(text), 
                "rep": str(rep), 
                "ret": str(ret), 
                "fav": str(fav), 
                }
         
            
            tweet_list.append(tweet_dict)
         
            
            
            
            
            """
            wks.update_acell('A' + str(count), str(day))
            time.sleep(1.1)
            wks.update_acell('B' + str(count), str(tim))
            time.sleep(1.1)
            wks.update_acell('C' + str(count), str(user_name))
            time.sleep(1.1)
            wks.update_acell('D' + str(count), str(user_id))
            time.sleep(1.1)
            wks.update_acell('E' + str(count), str(text))
            time.sleep(1.1)
            wks.update_acell('F' + str(count), str(rep))
            time.sleep(1.1)
            wks.update_acell('G' + str(count), str(ret))
            time.sleep(1.1)
            wks.update_acell('H' + str(count), str(fav))
            time.sleep(1.1)
            """
            
            
            
           # if tweet_num <= 0:
           #    break
                
          
    #error handling  
        except (AttributeError, TypeError, KeyError, ValueError):
            print("missing_value")
            #tweet_num += 1
            continue
        
        df = pd.DataFrame(tweet_list)
        df.to_excel('C:/Users/Ryutaro Takanami/.spyder-py3/WONGOO_FES/WGtweet.xlsx', sheet_name='new_sheet_name')
                
    

    return 

    
#tip the domino
if __name__ == "__main__":
    blogxtract(url)
    print("finish")









