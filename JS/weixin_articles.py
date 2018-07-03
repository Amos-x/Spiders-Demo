import requests
from bs4 import BeautifulSoup
import pymongo
import time

client = pymongo.MongoClient('localhost')
db = client.weixin
table = db.weixin_articles

url = 'http://weixin.sogou.com/weixin'
headers = {
    'Cookie':'ABTEST=0|1496493857|v1; SNUID=64FC6192E6E0B4EB462D9041E6B349FA; IPLOC=CN4404; SUID=811A8477771A910A000000005932AF21; JSESSIONID=aaaTrOP7BxqcE6-vuDIXv; SUV=009C7A5D77841A815932AF21F2375449; SUID=811A84773108990A000000005932AF5A; weixinIndexVisited=1; ppinf=5|1496493978|1497703578|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToyNzolRTUlQTQlOEYlRTUlODYlQUMlRTQlQjglQjZ8Y3J0OjEwOjE0OTY0OTM5Nzh8cmVmbmljazoyNzolRTUlQTQlOEYlRTUlODYlQUMlRTQlQjglQjZ8dXNlcmlkOjQ0Om85dDJsdU5aUnhtOUpIU2pSOXpkbVRIU1FSYU1Ad2VpeGluLnNvaHUuY29tfA; pprdig=BbejbchjRHoxXBRbUqqnl3xOe6RdvHzquIiD7MMagXIDALOwPfd4nX4ZFAB1gLG1iY0m1viw0UbzsJlUaZwnBULPsNUf9hgH0_1uYnGPyDq9diAGJOuZkWrvRFeUaynu0G8iJWzm-HCPl6EAjZ145GDAZA7Uv_fMdDNmaP7zYZU; sgid=03-26785975-AVkyr5oXAFZ4mwSGRwDkq7U; ppmdig=149649397800000045db757ae6ffaf262c2e2f9ef68bcc85; sct=1',
    'Host':'weixin.sogou.com',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}
proxy = None

def get_html(keyword,page_num):
    global proxy
    try:
        params = {
            'query': keyword,
            'type': '2',
            'page': page_num,
            'ie': 'utf8'
        }
        if proxy:
            proxies = {'http': proxy}
            response = requests.get(url, params=params, headers=headers, allow_redirects=False,proxies=proxies,timeout=20)
        else:
            response = requests.get(url,params=params,headers=headers,allow_redirects=False)
        if response.status_code == 200:
            print('正在抓取页数：',page_num)
            return response.text
        else:
            # need Porxy
            print(response.status_code)
            proxy = get_proxy()
            if proxy:
                print('use proxy:',proxy,'   抓取页数:',page_num)
                return get_html(keyword,page_num)
            else:
                print('no proxy，抓取失败')
                return None
    except :
        proxy = get_proxy()
        print('代理连接失败,重新使用新代理：',proxy,'   抓取页数：',page_num)
        return get_html(keyword,page_num)

def get_proxy():
    try:
        response = requests.get('http://localhost:5000/get')
        if response.status_code == 200:
            return response.text
        return None
    except:
        return None


def index_url(html):
    if html:
        soup = BeautifulSoup(html,'lxml')
        href = [x.attrs['href'] for x in soup.select('.news-list li .txt-box h3 a')]
        for i in href:
            data = analysis_articles(i)
            if data:
                table.insert(data)

def analysis_articles(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text,'lxml')
        result = {
            'time':soup.select('em#post-date')[0].get_text(),
            'wechat_pubilc_name':soup.select('div.rich_media_meta_list a')[0].get_text(),
            'wechat_num':soup.select('div.profile_inner span.profile_meta_value')[0].get_text(),
            'title':soup.select('h2.rich_media_title')[0].get_text().strip(),
            'article_body':soup.select('div.rich_media_content')[0].get_text(),
            'img':[x.attrs['data-src'] for x in soup.select('div.rich_media_content img')]
        }
        return result
    except:
        return None

def main(i):
    html = get_html('旅游', i)
    index_url(html)
    print(i,'  页抓取完毕')

if __name__ == '__main__':
    table.remove()
    t1 = time.time()
    for x in range(1,101):
        main(x)
    t2= time.time()
    print(t2-t1)