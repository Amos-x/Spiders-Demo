# __author__ = "Amos"
# Email: 379833553@qq.com

import requests
import time,logging
import execjs
import re
from bs4 import BeautifulSoup
from urllib.request import urljoin

logger = logging.getLogger(__name__)


class GetCookieBase(object):

    def crack_jiasule(self,url):
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'}
        resp = requests.get(url,headers=header)
        sHtmlJs = resp.text
        sHtmlJs = sHtmlJs.replace("eval", "return ")
        sHtmlJs = sHtmlJs.replace("<script>", "")
        sHtmlJs = re.sub("</script>.*", "",sHtmlJs)
        sHtmlJs = "function getResult(){%s}" %sHtmlJs.strip()
        sResult = execjs.compile(sHtmlJs).call('getResult')
        sResult = sResult.replace('while(window._phantom||window.__phantomas){};','')
        sResult = re.sub(r"var h=document.*toLowerCase\(\);","var h='%s';" %url.lower()[7:], sResult)
        sResult = re.sub(r"setTimeout.*",'return dc;};',sResult)
        jsl = execjs.compile(sResult).call('l')
        cookie = '__jsluid=%s; %s' %(resp.cookies.get('__jsluid'), jsl)
        headers = {
            'Cookie': cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            logger.info('破解加速乐反爬机制成功，返回cookie')
            print('破解加速乐反爬机制成功，返回cookie')
            com_cookie = '%s; JSESSIONID=%s; tlb_cookie=%s' % (cookie,response.cookies.get('JSESSIONID'),response.cookies.get('tlb_cookie'))
            return com_cookie
        else:
            logger.info('破解加速乐反爬机制失败，重试')
            print('破解加速乐反爬机制失败，重试')
            return self.crack_jiasule(url=url)

    def crack_jiyan(self,result):
        params = {
            'user': 'Amos',
            'pass': '379833553',
            'gt': result.get('gt'),
            'challenge': result.get('challenge'),
            'referer': 'http://www.gsxt.gov.cn',
            'return': 'json',
            'model': 3,
            'format':'utf8'
        }
        url = 'http://jiyanapi.c2567.com/shibie'
        response = requests.get(url,params=params,timeout=60)
        return response.json()


class GSXTGetCookie(GetCookieBase):

    def __init__(self):
        self.cookie_path = 'C:\\Users\Amos\PycharmProjects\Public_Opinion\gsxt_cookie'
        self.url = 'http://www.gsxt.gov.cn/SearchItemCaptcha?t={t}'.format(t=int(time.time() * 1000))
        with open(self.cookie_path,'r') as f:
            self.cookie = f.read()

    def save_cookie(self):
        cookie = self.crack_jiasule(url=self.url)
        with open(self.cookie_path,'w+') as f:
            f.write(cookie)
        self.cookie = cookie
        logger.info('写入cookie')
        print('写入cookie')

    def crack(self):
        headers = {
            'Cookie': self.cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
        }
        response = requests.get(self.url, headers=headers)
        if response.status_code == 200:
            result = self.crack_jiyan(response.json())
            if result.get('status') == 'ok':
                logger.info('破解极验验证码成功，返回结果')
                print('破解极验验证码成功，返回结果')
                result['cookie'] = self.cookie
                logger.info('破解GSXT国家企业信用信息公示系统反爬机制成功，返回参数')
                print('破解GSXT国家企业信用信息公示系统反爬机制成功，返回参数')
                return result
            elif result.get('status') == 'no':
                logger.info('破解极验验证码失败，重试')
                print('破解极验验证码失败，重试')
                return self.crack()
        elif response.status_code == 521:
            self.save_cookie()
            return self.crack()


if __name__ == '__main__':
    a = GSXTGetCookie()
    b = a.crack()
    if b.get('status') == 'ok':
        headers = {
            'Cookie': b.get('cookie'),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
        }
        data = {
            'tab': 'ent_tab',
            'province':'',
            'geetest_challenge': b.get('challenge'),
            'geetest_validate': b.get('validate'),
            'geetest_seccode': '%s|jordan' %b.get('validate'),
            'searchword': '芯智慧'
        }
        search_url = 'http://www.gsxt.gov.cn/corp-query-search-1.html'
        response = requests.post(search_url,data=data,headers=headers)
        soup = BeautifulSoup(response.text,'lxml')
        items = soup.select('a.search_list_item.db')
        for item in items:
            name = item.select('h1')[0].get_text().strip()
            url = urljoin(search_url,item.get('href'))
            response = requests.get(url,headers=headers)
            print(response.url)
            print(response.status_code)

        # 'http://www.gsxt.gov.cn/%7BA8E007D6CF86F65B23F2ADE49CF54A538240F880C90B62B1561F06D715795687D81A73A0470EB61B0118B5AF1748F0B9849F68B799569A7AB542B4549B70D260D28AD28AD28AC21910A2EAB2A8E1B962074F06DD85DD85CCB4ECB4672EF3FA296139164E471FC41F7AB0A31C70733C442D920F50493176AD769AC2BC04A9B30BC9760E4992CA92CA92CA-1521167374716%7D'

