import threading
import logging
import time
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import re
import cv2
import pytesseract
import numpy as np
import base64
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException 
from tencentcloud.ocr.v20181119 import ocr_client, models

def img_line(ImagePath,fileName):
    # 读取图片
    image = cv2.imread(ImagePath, 1)
    # 把图片转换为灰度模式
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 图像二值化
    ret, thresh1 = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
    # 进行两次中值滤波
    blur = cv2.medianBlur(thresh1, 3)  # 模板大小3*3
    blur = cv2.medianBlur(blur, 3)  # 模板大小3*3

    h, w = gray.shape
    #计算平均行像素值
    su=0
    for colo in range(h-1):
        su+=np.mean(blur[colo, :])
    f=su/(h-1)

    # 横向直线列表
    horizontal_lines = []
    flag=False
    s=0
    e=0
    for i in range(100,h - 1):
        # print(np.mean(blur[i, :]))
        if(np.mean(blur[i, :])>f):
            if flag:
                e=i
            else:
                flag=True
                s=i
                e=i
        else:
            if flag:
                flag=False
                horizontal_lines.append((s+e)/2)
    #划线
    for ii in horizontal_lines:
        i=int(ii)
        cv2.line(image, (0, i), (w, i), (0, 0, 0), 1)
    
    cv2.imwrite('./img_line/'+fileName, image)
    return horizontal_lines

def tx_ocr(filePath,fileName):
    # 实例化一个认证对象，入参需要传入腾讯云账户secretId，secretKey
    cred = credential.Credential("AKIDoPltlNQxwfdPxFP5h7qwFLCojSvDC5f3", "5wsZ5L1Vq0zlHYeV6yfGdkcFdmjTxCG6")

    httpProfile = HttpProfile()
    httpProfile.endpoint = "ocr.tencentcloudapi.com"
    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    client = ocr_client.OcrClient(cred, "ap-guangzhou", clientProfile)

    req = models.TableOCRRequest()
    path=filePath
    with open(path,"rb") as f:#转为二进制格式
        base64_data = base64.b64encode(f.read())#使用base64进行加密
    params=base64_data.decode('utf-8')
    req.ImageBase64=str(params)

    resp = client.TableOCR(req) 
    data=base64.b64decode(resp.Data)
    path='./res_xlsx/'+fileName+'.xlsx'
    with open(path,"wb")as f:
        f.write(data)
    f.close
    print('xlsx successed')

class Spider(object):

    def __init__(self,logger):
        self.logger=logger

    def handle_request(self,url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        }
        return urllib.request.Request(url=url, headers=headers)

    def get_image(self,url,pName):
        try:
            request = self.handle_request(url)
            response = urllib.request.urlopen(request)
            get_img = response.read()
            fp=open('./img/'+pName,'wb')
            fp.write(get_img)
            fp.close()
        except:
            print('no images found')

    def get_context(self,url):
        request = self.handle_request(url)
        content = urllib.request.urlopen(request).read().decode('utf-8')
        soup = BeautifulSoup(content, 'lxml')
        cont1 = soup.find_all(class_ = 'col-md-3')
        cont2 = soup.find_all(class_ = 'col-md-9')
        string = ''
        for x,y in zip(cont1,cont2):
            string+=x.text+':'+y.text+'\n'
        img=soup.select('div[id=content_main] > p > img')
        string+="imgName:"+img[0]['oldsrc']+'\n'
        string+="imgUrl:"+url.split('/t')[0]+'/'+img[0]['oldsrc']+'\n'
        self.get_image(url.split('/t')[0]+'/'+img[0]['oldsrc'],img[0]['oldsrc'])
        img_line('./img/'+img[0]['oldsrc'],img[0]['oldsrc'])
        tx_ocr('./img_line/'+img[0]['oldsrc'],img[0]['oldsrc'])
        return string

    def get_herf(self,url):
        request = self.handle_request(url)
        content = urllib.request.urlopen(request).read().decode('utf-8')
        soup = BeautifulSoup(content, 'lxml')
        href_list = soup.find_all(class_='list-group-item')
        return href_list


    def spider(self,url):
        #print('spider start at '+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        self.logger.info('spider start')       
        maxPage=9
        fp = open('res.txt', 'w', encoding='utf8')
        self.logger.info('file open succesed')
        cnt = 1
        for num in range(maxPage+1):
            if num==0:
                herf_list=self.get_herf('http://www.mot.gov.cn/tongjishuju/gonglu/index.html')
            else:
                herf_list=self.get_herf(url+'_%d'%num+'.html')
            for oa in herf_list:
                try:
                    href = oa['href']
                    context=self.get_context(href)
                    string ='PageUrl:'+href+'\n'+context+'\n'
                    fp.write(string)
                    self.logger.info('Total %d pages finished' %cnt)
                    cnt+=1
                    time.sleep(0.1)
                except Exception as e:
                    self.logger.error(e)
            self.logger.info("Page %d finished"%num)
            # break
        fp.close()
        self.logger.info('Finished')


if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    spi=Spider(logger)
    mainUrl='http://www.mot.gov.cn/tongjishuju/gonglu/index'
    spi.spider(mainUrl)
    print('main finished')

