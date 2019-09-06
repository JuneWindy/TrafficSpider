import threading
import logging
import time
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import re

class Spider(object):
    '''
    #待对接任务
    def __init__(self, logger, create_task_handle, data):
        self.logger = logger
        self.create_task_handle = create_task_handle
        self.data = data

    def process(self, source_url):
        self.logger.info('spider activate')
        self.data['test'] = time.time()
        self.create_task_handle({
             'source': 'xxx.com',
             'spider_id': -1
         })
        return {
            'content': 'abcde'
        }
    '''
    def __init__(self,logger):
        self.logger=logger

    def handle_request(self,url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        }
        return urllib.request.Request(url=url, headers=headers)

    def get_range(self,url):
        request = self.handle_request(url)
        content = urllib.request.urlopen(request).read()
        soup = BeautifulSoup(content, 'lxml')
        a=soup.find('a',text='末页')
        maxPage=int(a['href'].split('.')[0].split('_')[3])
        self.logger.info('maxPage is %d'%maxPage)
        return maxPage
    
    def get_city(self,url):
        request = self.handle_request(url)
        content = urllib.request.urlopen(request).read()
        soup = BeautifulSoup(content, 'lxml')
        a=soup.find(class_='city')
        city = a.text
        self.logger.info('Now city is %s'%city)
        return city

    def get_context(self,url):
        request = self.handle_request(url)
        content = urllib.request.urlopen(request).read().decode('utf-8')
        soup = BeautifulSoup(content, 'lxml')
        cont = soup.find(class_ = 'content')
        lead = soup.find(class_ = 'leading')
        string = ''
        if lead is not None:
            string +=lead.text
            string += '\n'
        if cont is not None :
            string +=cont.text.replace('手机访问 %s本地宝首页'%self.city,'')
            string += '\n'
        return string

    def get_herf(self,url):
        request = self.handle_request(url)
        content = urllib.request.urlopen(request).read().decode('utf-8')
        soup = BeautifulSoup(content, 'lxml')
        href_list = soup.find_all(class_='J-share-a')
        return href_list


    def spider(self,url):
        #print('spider start at '+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        self.logger.info('spider start')       
        firstPage=url+'1.htm'
        maxPage=self.get_range(firstPage)
        self.city=self.get_city(firstPage)
        fp = open('bdb_%s_road.txt'%self.city, 'w', encoding='utf8')
        self.logger.info('file open succesed')
        cnt = 1
        for num in range(1,maxPage+1):
            herf_list=self.get_herf(url+'%d'%num+'.htm')
            for oa in herf_list:
                try:
                    title = oa.string
                    href = oa['href']
                    context=self.get_context(href)
                    string ='new '+ '%d' %cnt + ':\n' + title + '\n' + context + '\n'
                    fp.write(string)
                    self.logger.info('total %d news finished' %cnt)
                    cnt+=1
                except Exception as e:
                    self.logger.error(e)
            self.logger.info("page %d finished"%num)
            #break
        fp.close()
        self.logger.info('finished')


if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    spi=Spider(logger)
    spi.spider('http://dg.bendibao.com/traffic/list_22_745_')
    print('main finished')

'''
可使用的url：
公交相关：
广州：http://jt.gz.bendibao.com/news/list_41_539_  1499
上海：http://sh.bendibao.com/traffic/list_23_608_  625条
东莞：http://dg.bendibao.com/traffic/list_22_745_  82
交通总相关：
上海：http://sh.bendibao.com/traffic/list_23_333_
北京：http://bj.bendibao.com/news/list_17_175_    3038条
'''


