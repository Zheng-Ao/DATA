
from tracemalloc import start
import requests
from bs4 import BeautifulSoup
import re

# import csv
import pandas as pd
from tqdm import tqdm
# import time

class paDloader:

    def __init__(self):
        self.path = "/Users/zhengao/Documents/Data/techMining"

        self.headers = {'User-Agent': 'Mozilla/5.0'}

        self.n_per_page = 50

        self.const_getPNs = "https://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2FPTO%2Fsearch-adv.htm&r=0&f=S&l=50&Query=ABST%2F%28%22artificial+intelligence%22%29&d=PTXT&p="
        self.const_gethtmls = {'pre1' :"https://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO1&Sect2=HITOFF&d=PALL&p=1&u=%2Fnetahtml%2FPTO%2Fsrchnum.htm&r=1&f=G&l=50&s1=",\
            'pre2' : ".PN.&OS=PN/",\
                'pre3' :"&RS=PN/"}
        self.const_getRefs = 'https://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2Fsearch-adv.htm&r=0&f=S&l=50&d=PALL&p=1&Query=ref/'
        self.const_getRefs_s = 'https://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2Fsearch-adv.htm&r=0&f=S&l=50&d=PALL&Query=ref/'


    def getHtmlDoc(self, const, var):
        # 标准爬虫程序

        try:
            var = str(var)
            url = const + var
            r = requests.get(url, timeout=360, headers=self.headers)
            r.raise_for_status
            return r.text
        except Exception as ex:
            print("{}采集出错，出错原因：{}".format(var, ex))
            return ""

    def getPageNum(self, const):
        html = self.getHtmlDoc(const, 1)
        soup = BeautifulSoup(html, "html.parser")
        n_str = soup.find_all(text = re.compile('patents.'))[0].text
        start = n_str.find(':')
        end = n_str.find('p')
        n = int(n_str[start+2:end-1])
        n_page = int(n/self.n_per_page)+1

        return n_page


    def getPNs(self, n_page, start=100, step=-2):

        # 获取pn_ls，通过制定start和step进行增量化数据存储
        
        end = start + step

        ls = []

        for i in tqdm(range(start, end, -1)):
            html = self.getHtmlDoc(self.const_getPNs, i)
            soup = BeautifulSoup(html, "html.parser")
            

            for item in soup.find_all(text = re.compile("\d"), href = re.compile("Parser?")):
                if len(item.text) < 11:
                    PN = item.text        
                    ls.append(PN)

        ls = pd.DataFrame(ls)
        ls.to_csv("PNs/"+str(end)+".csv")



    def getHtmls(self, pn_ls):
        
        # 获取html，通过pn_ls来控制批量

        for pn in tqdm(pn_ls):
            try:
                var = str(pn)
                url = self.const_gethtmls['pre1'] + var + self.const_gethtmls['pre2'] + var + self.const_gethtmls['pre3'] + var
    
                r = requests.get(url, timeout=360, headers=self.headers)
                r.raise_for_status
                html = r.text
                path = '/Users/zhengao/Documents/Data/techMining/htmls/' + var + '.html' 
                with open(path,'w+') as file:
                    file.write(html)
                # time.sleep(3)
                
            except Exception as ex:
                print("{}采集出错，出错原因：{}".format(var, ex))


    def getRefHtmls(self, pn_ls):

        # 获取ref_html，通过pn_ls来控制批量
        '''
        不同于gethtmls(),ref_html存在多种情况。
        1. ref=0,此时还是会正常下载;
        2. ref=1,此时会直接跳到那个文档,因此没办法用正则表达式获取被引次数;
        '''

        for pn in tqdm(pn_ls):
            try:
                var = str(pn)
                url = self.const_getRefs + var
                r = requests.get(url, timeout=120, headers=self.headers)                # Slow
                r.raise_for_status
                html = r.text

                soup = BeautifulSoup(html, "html.parser")

                if soup.body == None:
                    '''
                    此时html只有head（其中包含了引用本专利的那个专利的url），在浏览器中打开则会自动跳转，爬虫不会。
                    可以直接在这里处理，但是我不这样做，
                    ref_html将只包含被引序列，不包含具体信息。
                    '''

                    path = '/Users/zhengao/Documents/Data/techMining/ref_htmls/' + var + '_ref_1' + '.html'
                    with open(path,'w+') as file:
                            file.write(html)

                else:

                    n_str = soup.find_all(text = re.compile('patents.'))[0].text
                    start = n_str.find(':')
                    end = n_str.find('p')
                    n = int(n_str[start+2:end-1])
                    n_page = int(n/self.n_per_page)+1                                                        

                        
                    for i in range(1, n_page+1):
                        
                        url = self.const_getRefs_s + var + "&p=" + str(i)
                        r = requests.get(url, timeout=120, headers=self.headers)                # Slow
                        r.raise_for_status
                        html = r.text
                        path = '/Users/zhengao/Documents/Data/techMining/ref_htmls/' + var + '_ref_' + str(i) + '.html'
                        with open(path,'w+') as file:
                            file.write(html)
                        
            except Exception as ex:
                print("{}采集出错，出错原因：{}".format(var, ex))

