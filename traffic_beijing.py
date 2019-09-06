# coding=utf-8
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import requests
import time

def handle_request(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    }
    return urllib.request.Request(url=url, headers=headers)

def get_context(url):
    request = handle_request(url)
    content = urllib.request.urlopen(request).read()
    soup = BeautifulSoup(content, 'lxml')
    cont = soup.find(class_ = 'article_cont')
    return cont

def get_list(page):
    url = 'http://www.bjbus.com/home/ajax_news_list.php'
    #请求头信息
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0",
        "referer": "http://www.bjbus.com/home/fun_news_list.php?uNewsType=1&uStyle=2&uSec=00000177&uSub=00000178",
        'x-requested-with': 'XMLHttpRequest'
    }
    #每个ajax请求要传递的参数
    data = {
        'txtPage': page,
        'txtDisplayRows': '9',
        'txtType': '1',
        'txtCode':'',
        'txtContainer':'content',
        'txtStyle': '2'
    }
    request = requests.post(url, data=data, headers=headers)
    soup = BeautifulSoup(request.text,'lxml')
    return soup.find_all(class_='title')

def main():
    url ='http://www.bjbus.com/home/'
    fp = open('beijing_road.txt', 'w', encoding='utf8')
    print('start')
    cnt=1
    for num in range(1,223):
        li=get_list(num)
        for oa in li:
            ur=url+oa.find('a')['href']
            cont=get_context(ur)
            if cont is not None:
                string='news{}: {}\n\n'.format(cnt,cont.text)
                fp.write(string)
                print('news %d finished'%cnt)
                cnt+=1
            else :
                print('fialed')
        print('page %d finished'%num)
    fp.close()
    print("total %d news" % (cnt-1))
    
if __name__ == '__main__':
    main()