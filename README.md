# crawlerPixiv
a python code to download the recommendation in the homepage  
##How to use(simplify):  

    import crPixiv  
    username="your username"  
    password="your password"  
    savepath="the path you'd like to save these pictures"  
    crPixiv.start(username,password,savepath)
  
then it will download the daily recommendation picture in the homepage into your savepath.  
**it will download the recommendation picture in the discovery page after __2019_7_21__**

##Warning:
  - I am a newbie who have just learned python for a week. I don't exatly understand how the functions I used in this file work, maybe they have different manifestations in different environment.  
  - My environment is: windows 64bit, Chrome 75.0.3770.142, PyCharm&Python 3.7.
  - For using selenium you should have a chromedriver. [Click here to download](https://sites.google.com/a/chromium.org/chromedriver/downloads)
  - It needs to import several other files, to be sure you have them.
     - list: requests, re, os, time, BeautifulSoup from bs4, Image from PIL, selenium, multiprocessing, queue, threading
  - Because there are some problems in the selenium when I use a 'headless' option, **it will show the browser when it tries to login Pixiv.**
  - Maybe it will be corrected in the future, vice versa.
  - It is **noisy**! I mean if you run this code, it will print lots of tips which I use to debug in the past.
  - It will download the same pictures if there this picture stay in the recommendation for more than once.
    - __It will not after 2019_7_21__
  - It can **not** download .gif.
  
##To use other functions in crPixiv:
  - if you get a link of thumnail whose url includes __'master'__ which has less pixel than an __'original'__ picture, you could use:

        originalUrl = crPixiv.turnMasterIntoOriginal(masterUrl)
   
   to get the originalUrl, then try to use:

        downloadUrl(originalUrl,savepath)
    
   to download it.  
   __Note__: the Note under this Note has been invalid since I change the logic inside the code after __2019_7_21__  
   __Note__: the thumnail is always a .jpg in its url. However, I will try different type(just .jpg and .png) and I will also delete the wrong format of image file.
  if you want to get more recommendation in the sametime, you could change this patameter:
    crPixiv.start(username,password,savepath,processNumber)
   Actully, I don't exactly know the max processNumber it can take, and as the warning mentioned, it may download the same pictures especailly if you have large processNumber, which defult to be 1.
   
##Improvement in the future(maybe):
  - To climb in the Pixiv. This version does not like a crawler, because I haven't try to step in other links, just standstill in the homepage
    - have changed the logic inside the code, it can explore more pictures in the Discovery Page in __2019_7_21__
  - To filter the repeat images. Maybe I will use database or MD5 or so.  
    -  competed in __2019_7_21__ branch
  - To hide the browser. 
  - To support download of .gif.
  - To get the cookie. If I do so, it could have a much faster speed. However, because I try a whole day and still haven't work it out, I use selenium for instead.
  
---
#use markdown edit this text
