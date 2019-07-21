# import webbrowser as wb
import requests as rq
# import urllib
# import matplotlib as mpl
# import matplotlib.image
# import matplotlib.pyplot
import re
import os
import time
from bs4 import BeautifulSoup
# import datetime
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import multiprocessing as mp
from queue import Queue
from threading import Thread

q = Queue()
driver = None
isLogin = False
Page = 2


def BS(text, al='html.parser'):
    return BeautifulSoup(str(text), al)


# def clickXpath(drixpath):

def getHtml(username, password):
    xpathForGetMore = '//*[@id="item-container"]/section[2]/section/ul[2]/li/a'
    xpathForLoadMore = '//*[@id="js-mount-point-discovery"]/div/div[2]/div/div[3]'
    if not isLogin:
        driver = getHomwPageDriver(username, password)
    else:
        driver.get('https://www.pixiv.net')
    # driver.set_window_size(1920,760)
    # time.sleep(5)
    driver.find_element_by_xpath(xpathForGetMore).click()
    for i in range(Page):
        driver.find_element_by_xpath(xpathForLoadMore).click()
    finish = False
    html = ""
    time.sleep(1)
    while not finish:
        if len(html) < len(driver.page_source):
            html = driver.page_source
            time.sleep(1)
        else:
            finish = True
    # driver.close()
    return html


def getHomwPageDriver(username, password):
    chromeOption = Options()
    chromeOption.add_argument('--headless')
    chromeOption.add_argument('--disable-gpu')
    chromeOption = None
    driver = webdriver.Chrome(options=chromeOption)
    driver.implicitly_wait(30)
    # driver.set_window_size(100,100)
    # driver.find_element_by_xpath().c
    return loginPixiv(driver, username, password)


def loginPixiv(driver, username, password):
    fail = 1
    while fail:
        try:
            url = "https://www.pixiv.net/"
            xpathLogin = '//*[@id="wrapper"]/div[3]/div[2]/a[2]'
            xpathUsername = '//*[@id="LoginComponent"]/form/div[1]/div[1]/input'
            xpathPasswords = '//*[@id="LoginComponent"]/form/div[1]/div[2]/input'
            xpathSubmit = '//*[@id="LoginComponent"]/form/button'
            driver.get(url)
            driver.find_element_by_xpath(xpathLogin).click()
            # driver.find_element_by_xpath(xpathUsername).clear()
            driver.find_element_by_xpath(xpathUsername).send_keys(username)
            # driver.find_element_by_xpath(xpathPasswords).clear()
            driver.find_element_by_xpath(xpathPasswords).send_keys(password)
            driver.find_element_by_xpath(xpathSubmit).click()
            fail = 0
        except NoSuchElementException as e:
            # time.sleep(0.5)
            print(e.msg)
            # driver.close()
            print('失败%d次' % fail)
            fail += 1
            # driver = webdriver.Chrome(options=chromeOption)

    tips = "login success"
    print(tips)
    return driver


def getAllLinkInHomePageHtml(html):
    soupHtml = BS(html)
    recommendPart = soupHtml.find('ul', {'class': '_image-items gtm-illust-recommend-zone'})
    soupRP = BS(recommendPart, 'html.parser')
    list = soupRP.find_all('li', {'class': 'image-item'})
    masterUrllist = []
    # pattern = re.compile('<img src="(https://.*.jpg)"')
    for each in list:
        img = BS(each).find('img')
        if img['src'][-3:] != 'gif':
            masterUrllist.append(img['src'])
    return masterUrllist


def getAllLinkInDiscoveryPageHtml(html):
    soupHtml = BS(html)
    divt = str(soupHtml.find('div', {'class': re.compile(r'gtm-illust-recommend-zone _3cRxPb5.*')}))
    pattern = re.compile(
        r'https://i.pximg.net/c/\d{1,3}x\d{1,3}/img-master/img/\d{4}/\d{2}/\d{2}/\d{2}/\d{2}/\d{2}/\d+_p0_master1200.jpg')
    masterUrllist = pattern.findall(divt)
    return masterUrllist


def isValid(fullPath):
    valid = True
    try:
        Image.open(fullPath).load()
    except OSError:
        valid = False
    return valid


def getPixivPic(picurl: str, secondTime=False):
    refmod = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='
    id = picurl.split('/')[-1].split('_')[0]
    tips = 'now we are tring to download the picture of id:' + id + '\n'
    print(tips)
    headers = {'referer': refmod + id}
    name = time.strftime("%Y_%m_%d_%H_%M_%S_", time.localtime()) + picurl.split('/')[-1]
    tips2 = 'requesting.....\n'
    print(tips2)
    res = rq.get(picurl, headers=headers)
    tips4 = 'response code:' + str(res.status_code)
    print(tips4)
    if res.status_code != 200 and not secondTime:
        newPicture = changeSuffix(picurl, 'jpg', 'png')
        res, name = getPixivPic(newPicture, secondTime=True)
    tips3 = 'finished!'
    print(tips3)
    return (res, name)


def addSlash(path):
    if path[-1] != '/' or path[-1] != '\\':
        if len(path.split('/')) > 1:
            path += '/'
        else:
            path += '\\'
    return path


def downLoadPicwithChunk(response, fullpath, chunk_size=128):
    with open(fullpath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            f.write(chunk)


def downLoadPic(response, fullname):
    tips = 'downloading......'
    downLoadPicwithChunk(response, fullname)


def herestheLink(url, path):
    res, name = getPixivPic(picurl=url)
    path = addSlash(path)
    fullname = path + name
    tips = 'we will store it as: ' + fullname + '\n'
    print(tips)
    downLoadPic(res, fullname)
    return fullname


def changeSuffix(oldUrl, oldSuffix, newSuffix):
    return oldUrl.replace(oldSuffix, newSuffix, 1)


def confirm(fullpath, oldUrl):
    # 检查格式
    brokenFlag = False
    newUrl = ""
    if not isValid(fullpath):
        if oldUrl[-3:] == 'jpg':
            tips1 = 'Well, it seems like it is not a jpeg format. I will try png format\n'
            print(tips1)
            brokenFlag = True
            os.remove(fullpath)
            newUrl = changeSuffix(oldUrl, 'jpg', 'png')
            if newUrl[-3:] == 'jpg':
                tips2 = 'there are more than one jpg string in this url!\n'
                print(tips2)
    else:
        tips3 = 'It is OK\n'
        print(tips3)
    return brokenFlag, newUrl


def findNext(url, path):
    # 获取编号
    NOpattern = re.compile(r'p(\d+)+.jpg')
    NO = int(NOpattern.findall(url)[0])
    NO += 1
    nextUrl = NOpattern.sub("p%d.jpg" % NO, url)
    filename = herestheLink(nextUrl, path)
    brokenFlag, newurl = confirm(filename, nextUrl)
    if brokenFlag:
        return False, url
    else:
        return True, nextUrl


def downloadUrl(url, path):
    tips = "now working at " + url
    print((tips))
    filename = herestheLink(url, path)
    brokenFlag, newurl = confirm(filename, url)
    if brokenFlag:
        newFilename = herestheLink(newurl, path)
        brokenFlag, newurl = confirm(newFilename, newurl)
        if brokenFlag:
            tips = 'I have no idea if it still uncorrect this time. Check your link, may be it is a .gif picture. \nMissing url: %s\n' % newurl
            print(tips)
    else:
        nextUrl = url
        next = True
        while next:
            next, nextUrl = findNext(nextUrl, path)
    return url


def useHtmlForDownload(html, path):
    print('have gotten html')
    masterUrlList = getAllLinkInDiscoveryPageHtml(html)
    if masterUrlList == None:
        print("can not analyze html")
        return "unfinish"
    pool = mp.Pool()
    for each in masterUrlList:
        originalUrl = turnMasterIntoOriginal(each)
        pool.apply_async(downloadUrl, args=(originalUrl, path,))
    pool.close()
    pool.join()
    return "finish"


def turnMasterIntoOriginal(masterUrl: str):
    sp = masterUrl.split('/')
    # print(sp)
    sp[3:5] = []
    # print(sp)
    sp[3] = 'img-original'
    prefix = '_'.join(sp[-1].split('_')[0:2])
    suffix = sp[-1].split('.')[-1]
    sp[-1] = prefix + '.' + suffix
    # print(sp)
    # sp.remove([])
    return '/'.join(sp)


def functionForDownload(path):
    tips = "now finding for prepared HTML"
    print(tips)
    # poolForT2 = mp.Pool(processes=5)

    # time.sleep(50)
    finish = 0
    testcnt = 0
    while 1:
        if not q.empty():
            print("test2")
            html = q.get().get()
            # print(html)
            os.makedirs(path + '\\', exist_ok=True)
            # p = mp.Process(target=useHtmlForDownload, args=(html, path,))
            # p.start()
            useHtmlForDownload(html, path)
            finish = 1
        else:
            if finish:
                break


def functionForGetHtml(username, password, processnumber=1):
    global q
    # processnumber = 1
    poolForT1 = mp.Pool(processes=processnumber)
    print("now in getHtml")
    for i in range(processnumber):
        htmlObj = poolForT1.apply_async(getHtml, args=(username, password,))
        q.put(htmlObj)


def functionForExist():
    startTime = time.time()
    shutdown = False
    while 1:
        print(("in t3"))
        if not qr.empty():
            qr.get()
        tips = "queue len = " + str(q.__sizeof__())
        print(tips)
        tips2 = q.get()
        print(tips2)
        duration = time.time() - startTime
        if duration > 1800:
            shutdown = True
        if shutdown:
            t1.close()
            while not q.empty():
                a = 1
            t2.close()
            break


def start(username, password, path, processNumber=1):
    t1Break = False
    t2Break = False

    t1 = Thread(target=functionForGetHtml, args=(username, password, processNumber,))
    t2 = Thread(target=functionForDownload, args=(path,))
    # t3 = Thread(target=functionForExist)

    t1.start()
    t2.start()
    # t3.start()

    t1.join()
    t2.join()
    # t3.join()


if __name__ == '__main__':
    username = ""
    password = ""
    path = ""
    start(username, password, path)
    # getHtml(username,password)
