import threading
import logging
import time
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import re

class Spider(object):

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
        if a is not None:      
            maxPage=int(a['href'][4:-4])
            self.logger.info('maxPage is %d'%maxPage)
            return maxPage
        else :
            return 1
    
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
        self.city=self.get_city(firstPage).replace(' ','')
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
    spi.spider('http://cs.bendibao.com/traffic/gongjiao/list')
    print('main finished')

'''
可使用URL：
公交相关：
武汉：http://wh.bendibao.com/traffic/wuhangongjiao/list  350
天津：http://tj.bendibao.com/traffic/tiangongjiao/list  85
沈阳：http://sy.bendibao.com/traffic/sygongjiao/list 52
西安：http://xa.bendibao.com/traffic/xagongjiao/list 88
成都：http://cd.bendibao.com/traffic/chengdugongjiao/list 160
杭州：http://hz.bendibao.com/traffic/hzgongjiao/list 387
长沙：http://cs.bendibao.com/traffic/gongjiao/list 136
'''