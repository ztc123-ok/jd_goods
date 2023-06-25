import random
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from lxml import etree
import requests
import pandas as pd
import re
from time import sleep
from get_user_agent import get_user_agent_of_pc
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 进入某商品页爬取数据
def get_comment(href,name):
    chrome_driver = "C:/Users/周/Desktop/selenium_example/chromedriver_win32/chromedriver.exe"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("disable-infobars")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("user-agent=" + get_user_agent_of_pc())
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    s = Service(executable_path=chrome_driver)
    chrome2 = webdriver.Chrome(options=options, service=s)
    chrome2.maximize_window()
    chrome2.get(href)
    sleep(8+random.random())
    print("正在爬取评论...网址：",href)
    scroll(chrome2) # 滑到评论处，有些不准

    # 控制按钮进行点击,一定要点一下啊，不然不加载出来
    # 等待网页加载，防止网页加载过慢
    try:
        WebDriverWait(chrome2, timeout=5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="detail"]/div[1]/ul/li[5]'))).click()
        sleep(1+random.random())
        WebDriverWait(chrome2, timeout=5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="comment"]/div[2]/div[2]/div[1]/ul/li[1]/a'))).click()
        sleep(1+random.random())
    except Exception as e:
        print("评论区未点击")

    # 获取评论区下一页按钮信息
    js = 'return document.getElementsByClassName("ui-pager-next").length'
    first_next = chrome2.execute_script(js)
    has_next = first_next
    print("first_next", str(first_next))

    next_html = chrome2.page_source
    print("正在爬取  第{}页  评论...".format(1))
    parse_html_comment(next_html, name)
    num = 1
    # 当下一页按钮信息与第一页不同，结束爬取
    while has_next>=first_next:
        sleep(2 + random.random())
        try:
            next_page_buttun = chrome2.find_elements(by=By.CSS_SELECTOR, value='a.ui-pager-next')
            chrome2.execute_script('window.scrollTo(0,document.body.scrollHeight*0.92);')#需要滑倒按钮的位置
            sleep(1 + random.random())
            print("next_buttun长度", len(next_page_buttun))
            chrome2.execute_script("arguments[0].click();", next_page_buttun[0])#有东西阻挡的解决方式
            # next_page_buttun[0].click()
        # 网络或定位问题保存商品的网址
        except Exception as e:
            print("未定位到")
            with open("D:/爬取数据/test1/data/评论/erro.txt", "a+") as f:
                f.write(href+"\n")
            break
        num+=1
        print("正在爬取  第{}页  评论...".format(num))
        sleep(2+random.random())
        next_html = chrome2.page_source
        parse_html_comment(next_html,name)
        js = 'return document.getElementsByClassName("ui-pager-next").length'
        has_next = chrome2.execute_script(js)
        print("first_next:",first_next,"has_next:",has_next)
        # 评论区最多展示100页
        if num > 100:
            break


# 模拟向下滑动页面
def scroll(chrome):
    a = 0
    slices = 0
    delta = 0.06 + 0.1*random.random()
    b = a + delta*up()
    js = "window.scrollTo(document.body.scrollHeight*{},document.body.scrollHeight*{})"
    while b<=0.97:
        chrome.execute_script(js.format(a,b))
        sleep(0.5+random.random())
        a = b
        b = a+delta
        slices = slices+1
    if b>0.97:
        chrome.execute_script(js.format(a,0.97))
        slices = slices + 1
        sleep(0.5+random.random())

    print("分了{}个分区".format(slices))

def up():
    ud = [1,-1,1,1]
    return random.choice(ud)

# 解析商品评论信息
def parse_html_comment(html,name):
    tree = etree.HTML(html)
    comments_uname = tree.xpath("//div[@id='comment-0']/div/div[1]/div[1]/text()")
    comments_detail = tree.xpath("//p[@class='comment-con']")
    unames = [i for i in comments_uname if re.sub('\s+','',i) != '']
    print("uname:", unames)
    print("comments:", comments_detail)
    for per_comment, per_uname in zip(comments_detail, unames):
        name = re.sub('\/+','',name)
        name = re.sub('\*+','',name)
        name = re.sub('\|+','',name)
        name = re.sub('\\\+','',name)
        name = re.sub('\<+','',name)
        name = re.sub('\>+','',name)
        name = re.sub('\?+','',name)
        name = re.sub('\s+','',name)
        name = re.sub('\"+', '', name)
        with open('D:/爬取数据/test1/data/评论/{}.csv'.format(name), 'a+', encoding='utf8') as f:
            f.write("买家id："+re.sub('\s+','',per_uname)+','+"评论："+per_comment.text+"\n")


if __name__=="__main__":
    start = time.time()
    headers={
        'user-agent':get_user_agent_of_pc(),
        'Connection':'close'
    }
    # href = ["https://item.jd.com/100045165277.html"]
    # name = ["a"]
    # 爬取商品时的信息
    df = pd.read_csv('D:/爬取数据/test1/data/手机.csv',header=None,error_bad_lines=False,encoding="utf8")
    href = [i.split("：")[1] for i in df[1]]
    name = [i.split("：")[1] for i in df[0]]
    print(href[0:3])
    print(name[0:3])
    print("href:",len(href))
    print("name:",len(name))
    # 可选取想爬取的商品
    for per_href,per_name in zip(href[:],name[:]):
        get_comment(per_href,per_name)
        sleep(2+random.random())
    end=time.time()
    print('爬取评论时间%.4f'%(end-start))