from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import  WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pymongo
import time
from multiprocessing import Pool

client = pymongo.MongoClient('localhost')
db = client.taobao
table = db.taobao_meishi
service_args = ['--load-images=false','--disk-cache=true']
browser = webdriver.PhantomJS(service_args=service_args)
wait = WebDriverWait(browser,10)
browser.set_window_size(1400,900)

def search():
    print('正在搜索')
    try:
        browser.get('https://www.taobao.com/')
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#q')))
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J_TSearchForm > div.search-button > button')))
        input.send_keys('美食')
        button.click()
        total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.total')))
        firstpage = get_data()
        table.insert(firstpage)
        return total.text
    except TimeoutException:
        return search()

def next_page(page_num):
    print('正在翻页',page_num)
    try:
        browser.get('https://s.taobao.com/search?q=%E7%BE%8E%E9%A3%9F&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20170601&ie=utf8')
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        input.clear()
        input.send_keys(page_num)
        button.click()
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > ul > li.item.active > span'),str(page_num)))
        page_data = get_data()
        table.insert(page_data)
    except TimeoutException:
        next_page(page_num)

def get_data():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-itemlist .items .item')))
    soup = BeautifulSoup(browser.page_source,'lxml')
    items = soup.select('#mainsrp-itemlist .items div[data-category="auctions"]')
    for i in items:
        yield{
            'img':i.select('.pic img')[0].attrs['data-src'],
            'price':i.select('strong')[0].get_text(),
            'title':i.select('div[class="row row-2 title"] a')[0].get_text().strip(),
            'shop':i.select('div.shop a')[0].get_text().strip(),
            'location':i.select('div.location')[0].get_text(),
            'sales':i.select('div.deal-cnt')[0].get_text()[:-3]
        }

if __name__ == '__main__':
    t1 = time.time()
    pool = Pool()
    table.remove()
    total = search()
    total = int(total.strip()[2:5])
    pool.map(next_page,[x for x in range(2,total+1)])
    browser.close()
    t2 = time.time()
    print(t2-t1)