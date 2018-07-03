# -*- coding: utf-8 -*-
import scrapy
from Public_Opinion.captcha_crack import GSXTGetCookie
import requests
from bs4 import BeautifulSoup

class GsxtSpider(scrapy.Spider):
    name = 'gsxt'
    search_url = 'http://www.gsxt.gov.cn/corp-query-search-1.html'
    keywords = ['佛山科瑞森科技有限公司']

    def start_requests(self):
        gsxt = GSXTGetCookie()
        for keyword in self.keywords:
            result = gsxt.crack()
            headers = {
                'Cookie': result.get('cookie'),
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
            }
            data = {
                'tab': 'ent_tab',
                'province': '',
                'geetest_challenge': result.get('challenge'),
                'geetest_validate': result.get('validate'),
                'geetest_seccode': '%s|jordan' % result.get('validate'),
                'searchword': keyword
            }
            # TODO 这里不知为何，用formquest就是访问不成功
            # yield scrapy.FormRequest(self.search_url ,formdata=data, headers=headers,callback=self.parse)
            print('使用requests.post直接访问')
            response = requests.post(self.search_url,data=data,headers=headers)
            print(response.status_code)
            print(response.text)

    def parse(self, response):
        print(response.url)
        print(response.status_code)
