#!/usr/bin/python
# -*- encoding:utf-8 -*-

from urllib.request import urlopen, HTTPError
from bs4 import BeautifulSoup
import os
import threading

class ProgressBar(object):
    def __init__(self, title, count=0.0, run_status=None, fin_status=None, total=100.0, unit='', sep='/',
                 chunk_size=1.0):
        super(ProgressBar, self).__init__()
        self.info = "[%s] %s %d %s %s %d %s"
        self.title = title
        self.total = total
        self.count = count
        self.chunk_size = chunk_size
        self.status = run_status or ""
        self.fin_status = fin_status or " " * len(self.status)
        self.unit = unit
        self.seq = sep

    def __get_info(self):
        # [名称] 状态 进度 单位 分割线 总数 单位
        _info = self.info % (self.title, self.status, self.count / self.chunk_size, self.unit, self.seq, self.total / self.chunk_size, self.unit)
        return _info

    def refresh(self, count=1, status=None):
        self.count += count
        self.status = status or self.status
        end_str = "\r"
        if self.count >= self.total:
            end_str = '\n'
            self.status = status or self.fin_status
        print(self.__get_info(), end=end_str)


def getBookInfo(catalogUrl):
    chapterUrlList = []
    try:
        catalogHtml = urlopen(catalogUrl)
    except (HTTPError, ValueError) as e:
        print(u"小说目录访问错误：%s" % catalogUrl)
        exit(1)
    bsObj = BeautifulSoup(catalogHtml, features="lxml")
    try:
        bookName = bsObj.find("h1").get_text()
        catalogList = bsObj.find("dl").findAll("dd")
    except AttributeError:
        print(u"目录信息获取错误")
        exit(1)
    for chapter in catalogList:
        chapterUrlList.append(chapter.find("a")["href"])
    return bookName, chapterUrlList

def downloadChapter(chapterUrl):
    try:
        chapterHtml = urlopen(chapterUrl)
        bsObj = BeautifulSoup(chapterHtml, features="lxml")
        title = bsObj.find("h1").get_text()
        content = bsObj.find("div", {"id": "content"}).get_text()
    except (HTTPError, ValueError):
        print("章节获取错误: %s" % chapterUrl)
        return None, None
    return title, content

if __name__ == '__main__':
    download_path = "D:/Download"
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    # catalogUrl = "http://www.biquge.com.tw/19_19462/"
    print("---------------------------------------------")
    print("----------------笔趣阁小说下载-----------------")
    print("---------http://www.biquge.com.tw/-----------")
    print("---------------------------------------------")
    catalogUrl = str(input("请输入小说目录下载地址:\n"))
    book_name, chapterUrlList = getBookInfo(catalogUrl)
    progress = ProgressBar(title="下载进度",
                           run_status="正在下载",
                           fin_status="下载完成",
                           total=len(chapterUrlList),
                           unit="章",
                           chunk_size=1)
    with open(download_path + "/%s.txt" % book_name, "a", encoding='utf-8') as f:
        for chapterUrl in chapterUrlList:
            title, content = downloadChapter("http://www.biquge.com.tw" + chapterUrl)
            progress.refresh(count=1)
            f.write(title)
            f.write("\n")
            f.write(content)
            f.write("\n")
