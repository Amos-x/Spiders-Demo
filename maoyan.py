import requests
from bs4 import BeautifulSoup
import pymongo
import time
from multiprocessing import Pool

def spider(url):
    headers ={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    response = requests.get(url,headers=headers)
    soup = BeautifulSoup(response.content,'lxml')
    name = [x.get_text().strip() for x in soup.select('div.movie-item-info p.name')]
    star = [y.get_text().strip() for y in soup.select('div.movie-item-info p.star')]
    releasetime = [z.get_text().strip() for z in soup.select('div.movie-item-info p.releasetime')]
    score = [a.get_text().strip() for a in soup.select('p.score')]
    img = [b.attrs['data-src'] for b in soup.select('img.board-img')]
    for i in zip(name,star,releasetime,score,img):
        yield{
            'name':i[0],
            'star':i[1],
            'releasetime':i[2],
            'score':i[3],
            'img':i[4]
        }

client = pymongo.MongoClient('localhost')
db = client.maoyan
table = db.maoyao_TOP100

def main(x):
    print('页数:',x)
    url = 'http://maoyan.com/board/4?'+ 'offset=' + str(x)
    b = spider(url)
    table.insert(b)

if __name__ == '__main__':
    t1 = time.time()
    table.remove()
    aaa = list(range(10))
    pool = Pool()
    pool.map(main,[i*10 for i in range(10)])
    client.close()
    t2 = time.time()
    print(t2-t1)