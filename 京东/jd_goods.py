import random
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from lxml import etree
import requests
import re
from time import sleep
from get_user_agent import get_user_agent_of_pc
from selenium.webdriver.chrome.service import Service

def JDspider(url):
    chrome_driver = "C:/Users/周/Desktop/selenium_example/chromedriver_win32/chromedriver.exe"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("disable-infobars")
    options.add_argument("user-agent=" + get_user_agent_of_pc())
    options.add_experimental_option("excludeSwitches",["enable-automation"])
    s=Service(executable_path=chrome_driver)
    chrome=webdriver.Chrome(options=options,service=s)

    chrome.get(url)
    print("正在爬取第{}页...".format(1))
    time.sleep(3 + random.random())

    scroll(chrome)

    num = 1
    js = 'return document.getElementsByClassName("pn-next disabled").length'
    has_next = chrome.execute_script(js)

    while has_next==0:
        try:
            next_page_buttun = chrome.find_element(by=By.XPATH,value='//a[@class="pn-next"]')
            next_page_buttun.click()
        except Exception as e:
            break

        num+=1
        print("正在爬取第{}页...".format(num))
        sleep(1+random.random())
        scroll(chrome)
        next_html = chrome.page_source
        parse_html(next_html)
        js = 'return document.getElementsByClassName("pn-next disabled").length'
        has_next = chrome.execute_script(js)

def get_comment(href,name):
    chrome_driver = "C:/Users/周/Desktop/selenium_example/chromedriver_win32/chromedriver.exe"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("disable-infobars")
    options.add_argument("user-agent=" + get_user_agent_of_pc())
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    s = Service(executable_path=chrome_driver)
    chrome2 = webdriver.Chrome(options=options, service=s)

    chrome2.get(href)
    print("正在爬取评论...网址：",href)

    scroll(chrome2)

    next_html = chrome2.page_source
    parse_html_comment(next_html,name)
    js = 'return document.getElementsByClassName("ui-pager-next").length'
    has_next = chrome2.execute_script(js)
    num = 1

    while has_next>=1:
        try:
            next_page_buttun = chrome2.find_element(by=By.XPATH,value='//a[@class="ui-pager-next"]')
            next_page_buttun.click()
        except Exception as e:
            break
        sleep(1 + random.random())
        t = 0.97 + 0.01*random.random()
        js = "window.scrollTo(document.body.scrollHeight*{},document.body.scrollHeight*{})"
        chrome2.execute_script(js.format(t, t))
        num+=1
        print("正在爬取  第{}页  评论...".format(num))
        sleep(2+random.random())
        next_html = chrome2.page_source
        parse_html_comment(next_html,name)
        js = 'return document.getElementsByClassName("ui-pager-next").length'
        has_next = chrome2.execute_script(js)

    chrome2.quit()


def scroll(chrome):
    a = 0
    slices = 0
    delta = 0.06 + 0.1*random.random()
    b = a + delta*up()
    js = "window.scrollTo(document.body.scrollHeight*{},document.body.scrollHeight*{})"
    while b<=1:
        chrome.execute_script(js.format(a,b))
        sleep(0.5+random.random())
        a = b
        b = a+delta
        slices = slices+1
    if b>1:
        chrome.execute_script(js.format(a,1))
        slices = slices + 1
        sleep(0.5+random.random())

    print("分了{}个分区".format(slices))

def up():
    ud = [1,-1,1,1]
    return random.choice(ud)

def parse_html_comment(html,name):
    tree = etree.HTML(html)
    comments_uname = tree.xpath('//*[@id="comment"]/div[2]/div[2]/div[2]/div/div/div[1]/div[1]')
    comments_detail = tree.xpath('//*[@id="comment"]/div[2]/div[2]/div[2]/div/div/div[2]/p/text()')
    with open('D:/爬取数据/test1/data/评论/{}.csv'.format(name), 'a+', encoding='utf8') as f:
        for per_comment,per_uname in zip(comments_detail,comments_uname):
            f.write("买家id："+re.sub('\s+','',per_uname.xpath('string()'))+','+"评论："+per_comment+"\n")

def parse_html(html):
    tree = etree.HTML(html)
    names = tree.xpath('//*[@id="J_goodsList"]/ul/li/div/div[4]/a/em')
    prices = tree.xpath('//*[@id="J_goodsList"]/ul/li/div/div[3]/strong/i/text()')
    hrefs = tree.xpath('//*[@id="J_goodsList"]/ul/li/div/div[1]/a/@href')
    shops = tree.xpath('//*[@id="J_goodsList"]/ul/li/div/div[7]/span/a/text()')
    img_urls = tree.xpath('//*[@id="J_goodsList"]/ul/li/div/div[1]/a/img/@src')
    comments = tree.xpath('//*[@id="J_goodsList"]/ul/li/div/div[5]/strong/a/text()')

    for name,price,href,shop,comment,img_url in zip(names,prices,hrefs,shops,comments,img_urls):
        with open('D:/爬取数据/test1/data/手机.csv','a+',encoding='utf8') as f:
            f.write("商品名："+re.sub('\s+','',name.xpath('string()'))+','+
                "商品链接：" +"https:" + href+','+
                "价格：" +price +','+
                "卖家：" + shop + ","+
                "评论数："+comment+','+
                "图片链接："+"https:"+img_url+"\n"
                )
        response = requests.get('https:' + img_url,headers=headers,timeout=(3,7))

        img_name1=re.sub('\/+','',name.xpath('string()'))
        img_name2 = re.sub('\*+','', img_name1)
        img_name3 = re.sub('\|+','',img_name2)
        img_name4 = re.sub('\\\+','', img_name3)
        img_name5 = re.sub('\<+','', img_name4)
        img_name6 = re.sub('\>+','', img_name5)
        img_name7 = re.sub('\?+','', img_name6)
        img_name8 = re.sub('\s+','', img_name7)
        img_name9 = re.sub('\"+', '', img_name8)

        with open('D:/爬取数据/test1/images/{}.jpg'.format(img_name9),'wb') as f:
            f.write(response.content)

        #get_comment("https:"+href,re.sub('\s+','',name.xpath('string()')))

if __name__=="__main__":
    start = time.time()
    headers={
        'user-agent':get_user_agent_of_pc(),
        'Connection':'close'
    }
    first_page = "https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&wq=%E6%89%8B%E6%9C%BA&pvid=8858151673f941e9b1a4d2c7214b2b52"
    JDspider(first_page)
    end=time.time()
    print('爬取时间%.4f'%(end-start))