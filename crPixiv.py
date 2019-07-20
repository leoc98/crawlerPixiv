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


def BS(text, al='html.parser'):
    return BeautifulSoup(str(text), al)


def getHtml(username, password):
    driver = getDriver(username, password)
    # driver.set_window_size(1920,760)
    time.sleep(5)
    html = driver.page_source
    driver.close()
    return html


def getDriver(username, password):
    chromeOption = Options()
    chromeOption.add_argument('--headless')
    chromeOption.add_argument('--disable-gpu')
    chromeOption = None
    driver = webdriver.Chrome(options=chromeOption)
    # driver.set_window_size(100,100)
    return loginPixiv(driver, username, password)


def loginPixiv(driver, username, password):
    fail = 1
    while fail:
        try:
            driver.get("https://www.pixiv.net/")
            driver.find_element_by_link_text(u"登录").click()
            driver.find_element_by_xpath(
                u"(.//*[normalize-space(text()) and normalize-space(.)='忘记了'])[1]/following::input[1]").click()
            driver.find_element_by_xpath(
                u"(.//*[normalize-space(text()) and normalize-space(.)='忘记了'])[1]/following::input[1]").clear()
            driver.find_element_by_xpath(
                u"(.//*[normalize-space(text()) and normalize-space(.)='忘记了'])[1]/following::input[1]").send_keys(
                username)
            driver.find_element_by_xpath(
                u"(.//*[normalize-space(text()) and normalize-space(.)='忘记了'])[1]/following::input[2]").clear()
            driver.find_element_by_xpath(
                u"(.//*[normalize-space(text()) and normalize-space(.)='忘记了'])[1]/following::input[2]").send_keys(
                password)
            driver.find_element_by_xpath(
                u"(.//*[normalize-space(text()) and normalize-space(.)='忘记了'])[1]/following::button[1]").click()
            fail = 0
        except NoSuchElementException as e:
            # time.sleep(0.5)
            # print(e.msg)
            # driver.close()
            print('失败%d次' % fail)
            fail += 1
            # driver = webdriver.Chrome(options=chromeOption)

    tips = "login success"
    print(tips)
    return driver


def getAllLinkInHtml(html):
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


def isValid(fullPath):
    valid = True
    try:
        Image.open(fullPath).load()
    except OSError:
        valid = False
    return valid


def getPixivPic(picurl: str):
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
            newUrl = oldUrl.replace('jpg', 'png', 1)
            if newUrl[-3:] == 'jpg':
                tips2 = 'there are more than one jpg string in this url!\n'
                print(tips2)
    else:
        tips3 = 'It is OK\n'
        print(tips3)
    return brokenFlag, newUrl


def findNext(url, path):
    # 获取编号
    NOpattern = re.compile(r'p(\d)+.jpg')
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
    masterUrlList = getAllLinkInHtml(html)
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
            p = mp.Process(target=useHtmlForDownload, args=(html, path,))
            p.start()
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
    start(username, password, path)
