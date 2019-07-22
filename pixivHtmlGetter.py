from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time


class PixivHtmlGetter:
    '''
    use to open a driver to get Html
    '''
    xpathForGetMore = '//*[@id="item-container"]/section[2]/section/ul[2]/li/a'
    xpathForLoadMore = '//*[@id="js-mount-point-discovery"]/div/div[2]/div/div[3]'
    url = 'https://www.pixiv.net'
    xpathLogin = '//*[@id="wrapper"]/div[3]/div[2]/a[2]'
    xpathUsername = '//*[@id="LoginComponent"]/form/div[1]/div[1]/input'
    xpathPasswords = '//*[@id="LoginComponent"]/form/div[1]/div[2]/input'
    xpathSubmit = '//*[@id="LoginComponent"]/form/button'

    def __init__(self, username, password, morePage=0, driver=None, tipsOption=False):
        self.tipsOption = tipsOption
        self.driver = driver
        self.username = username
        self.password = password
        self.morePage = morePage
        self.finish = False
        self.option = Options()
        self.implicitly_wait = 30
        self.login = False
        self.html = ""

    def printTips(self, printOut):
        if self.tipsOption:
            print(printOut)

    def getHtml(self):
        if not self.login:
            self.driver = self.getHomwPageDriver()
            self.driver.find_element_by_xpath(PixivHtmlGetter.xpathForGetMore).click()
        else:
            self.driver.get(PixivHtmlGetter.url)
        for i in range(self.morePage):
            self.driver.find_element_by_xpath(PixivHtmlGetter.xpathForLoadMore).click()
        time.sleep(1)
        while not self.finish:
            if len(self.html) < len(self.driver.page_source):
                self.html = self.driver.page_source
                time.sleep(1)
            else:
                self.finish = True
        # driver.close()
        return self.html

    def getHomwPageDriver(self):
        self.driver = webdriver.Chrome(options=self.option)
        return self.loginPixiv()

    def loginPixiv(self):
        fail = 1
        while fail:
            try:
                self.driver.get(PixivHtmlGetter.url)
                self.driver.find_element_by_xpath(PixivHtmlGetter.xpathLogin).click()
                # driver.find_element_by_xpath(xpathUsername).clear()
                self.driver.find_element_by_xpath(PixivHtmlGetter.xpathUsername).send_keys(self.username)
                # driver.find_element_by_xpath(xpathPasswords).clear()
                self.driver.find_element_by_xpath(PixivHtmlGetter.xpathPasswords).send_keys(self.password)
                self.driver.find_element_by_xpath(PixivHtmlGetter.xpathSubmit).click()
                self.driver.implicitly_wait(self.implicitly_wait)
                fail = 0
            except NoSuchElementException as e:
                # time.sleep(0.5)
                self.printTips(e.msg)
                # driver.close()
                self.printTips('失败%d次' % fail)
                fail += 1
                # driver = webdriver.Chrome(options=chromeOption)

        tips = "login success"
        self.printTips(tips)
        return self.driver

    def __del__(self):
        self.driver.close()
