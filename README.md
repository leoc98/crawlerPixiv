# crawlerPixiv
a python code to download the recommendation in the homepage'\n'
How to use(simplify):
  import crPixiv
  username=""
  password=""
  savepath=""
  crPixiv.start(username,password,savepath)
then it will download the daily recommendation picture in the homepage into your savepath

Warning:
  I am a newbie who have just learned python for a week. I don't exatly understand how the functions I used in this file work, maybe they have different manifestations in different environment.
    My environment is: windows 64bit, Chrome 75.0.3770.142, PyCharm&Python 3.7.
    For using selenium you should have a chromedriver  downloadLink:https://sites.google.com/a/chromium.org/chromedriver/downloads
  It needs to import many other file, to sure you have them.
    list: requests, re, os, time, BeautifulSoup from bs4, Image from PIL, selenium, multiprocessing, queue, threading
  Because there are some problems in the selenium when I use a 'headless' option, it will show the browser when it tries to login Pixiv.
    Maybe it will be corrected in the future, vice versa.
  It is noisy! I mean if you run this code, it will print lots of tips which I use to debug in the past.
  It will download the same pictures if there this picture stay in the recommendation for more than once.
  It can not download .gif.
  
To use other functions in it:
  if you get a link of thumnail whose url includes 'master' which has less pixel than an 'original' picture, you could use:
    originalUrl = crPixiv.turnMasterIntoOriginal(masterUrl)
   to get the OriginalUrl, then try to use:
    downloadUrl(originalUrl,savepath)
   to download it.
   Note: the thumnail is always a .jpg in its url. However, I will try different type(just .jpg and .png) and I will also delete the wrong format of image file.
  if you want to get more recommendation in the sametime, you could change this patameter:
    crPixiv.start(username,password,savepath,processNumber)
   Actully, I don't exactly know the max processNumber it can take, and as the warning mentioned, it may download the same pictures especailly if you have large processNumber, which defult to be 1.
   
Improvement in the future(maybe):
  To climb in the Pixiv. This version does not like a crawler, because I haven't try to step in other links, just standstill in the homepage
  To filter the repeat images. Maybe I will use database or MD5 or so.
  To hide the browser. 
  To support download of .gif.
  To get the cookie. If I do so, it could have a much faster speed. However, because I try a whole day and still haven't work it out, I use selenium.
  
