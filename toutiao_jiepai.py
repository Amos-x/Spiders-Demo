import requests
import  pymongo
from hashlib import md5
from multiprocessing import Pool
import time

client = pymongo.MongoClient('localhost')
db = client.toutiao
table = db.toutiao_jiepai

def get_data(offset):
    url ='http://www.toutiao.com/search_content/'
    params = {
        'offset':offset,
        'format':'json',
        'keyword':'街拍',
        'autoload':'true',
        'count':'20',
        'cur_tab':'1'
    }
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    response = requests.get(url,params=params)
    if response.json()['data']:
        items = response.json()['data']
        all_result=[]
        for item in items:
            result = {
                'title':item['title'],
                'source':item['source'],
                'img':[x['url'] for x in item['image_detail']]
            }
            table.insert(result)
            all_result.append(result)
        return all_result

def download_img(all_result):
    for x in all_result:
        img_list = x['img']
        for url in img_list:
            response = requests.get(url)
            file_path = '{0}/{1}.{2}'.format('F:\img',md5(response.content).hexdigest(),'jpg')
            with open(file_path,'wb') as f:
                f.write(response.content)
                f.close()

def main(x):
    print('offset：',x)
    data = get_data(x)
    if data:
        download_img(data)

if __name__ =='__main__':
    t1 = time.time()
    table.remove()
    pool = Pool()
    pool.map(main,[i*20 for i in range(10)])
    t2 = time.time()
    print(t2-t1)