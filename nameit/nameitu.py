#!/usr/bin/python

import sys
import os

import re
import sys


def snapshot(file_name="snap.jpg",cam_n = 0):
    import cv2
    cam = cv2.VideoCapture(cam_n)
    
    taste = 0
    bild = cam.read()
    while taste <> ord(" "):
        ret, bild = cam.read()
        cv2.imshow("Hit [SPACE] to capture", bild)
        taste = cv2.waitKey(2) & 0xff
    
    cv2.imwrite(file_name,bild)
    
def curl_get(url):
    #print "getting ", url[-5:],
    #sys.stdout.flush()
    import pycurl
    try:
        #python3
        from io import BytesIO
    except ImportError:
        #python2
        from StringIO import StringIO as BytesIO
        
    try:
        # python 3
        from urllib.parse import urlencode
    except ImportError:
        # python 2
        from urllib import urlencode
    
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(curl.URL,url)
    curl.setopt(curl.WRITEFUNCTION, buffer.write)
    #Google is unsing a redirect page as reply 
    curl.setopt(curl.FOLLOWLOCATION, True)
    curl.setopt(curl.COOKIEJAR, "kekstopf")
    #Google does some filtering on the userangent (it does not like to be asked by CURL or just Mozilla/5.0)
    curl.setopt(curl.USERAGENT,'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.91 Safari/537.36')
    curl.perform()
    curl.close()

    return buffer.getvalue()
   



def nameitu(picture):
    #curl --trace-ascii trace -c kekstopf -L -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.91 Safari/537.36' -F encoded_image=@"$1" https://www.google.com/searchbyimage/upload

    import re
    import pycurl
    try:
        #python3
        from io import BytesIO
    except ImportError:
        #python2
        from StringIO import StringIO as BytesIO
        
    try:
        # python 3
        from urllib.parse import urlencode
    except ImportError:
        # python 2
        from urllib import urlencode
    
    buffer = BytesIO()
    curl = pycurl.Curl()
    
    #postdict=[("encoded_image", (curl.FORM_FILE,picture_file)),]
    
    #import StringIO
    #datastrbuff = StringIO.StringIO(databuff)
    
    #print img
    
    postdict=[("encoded_image", (pycurl.FORM_BUFFER, "picture", pycurl.FORM_BUFFERPTR, picture)),]
    curl.setopt(curl.URL,"https://www.google.com/searchbyimage/upload")
    curl.setopt(curl.WRITEFUNCTION, buffer.write)
    #Google is unsing a redirect page as reply 
    curl.setopt(curl.FOLLOWLOCATION, True)
    curl.setopt(curl.COOKIEJAR, "kekstopf")
    #Google does some filtering on the userangent (it does not like to be asked by CURL or just Mozilla/5.0)
    curl.setopt(curl.USERAGENT,'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.91 Safari/537.36')
    curl.setopt(curl.HTTPPOST,postdict)
    curl.perform()
    curl.close()
    
    databuff.close()
    
    page = buffer.getvalue()
    
    #export googles response (not the redirecht page)
    f = open("page.htm","w")
    f.write(page)
    f.close()
    
    #Regex for /search?q=neue+5+euro+schein& (which is the blue text link to search the image content @google)
    #<a class="_gUb" href="/search?q=neue+5+euro+schein&amp;sa=X&amp;ei=7GIdVfugMcGfsAHql4PYAg&amp;ved=0CB0QvQ4oAA" style="font-style:italic">neue 5 euro schein</a>
    
    #out=re.findall(r"\/search\?q=([^&]*)", page)
    out=re.findall(r"<a class=\"_gUb\" [^>]*>([^<]*)</a>", page)
    out1=re.findall(r"<h3 class=\"r\"><a href=\"([^\"]*)\"",page)
    out2=re.findall(r'http[^\"]*imgres[^\"]*',page)
    out3=re.findall(r'title="(htt[^"]*)', page)
    
    #what would google tag this?
    if len(out)<1:
      out=[]
    else:
      out=out[0]
      out=re.split('\W+',out,re.UNICODE)
    
    imgreses=60
    #find the  similar pictures link and follow
    if len(out2)<imgreses :
      simpage=re.search(r"\/search\?tbs=simg:[^\">]*",page).group(0)
      simpage=re.sub(r"&amp;","&", simpage)
      simpage=curl_get("https://www.google.com"+simpage)
      out2=re.findall(r'http[^\"]*imgres[^\"]*',simpage)
      
      
    #out4=[]
    #for i in out2:
      #if len(out4)>=imgreses:
        #break
      #i=re.sub(r"&amp;","&", i)
      ##print i
      #print ".",
      #sys.stdout.flush()
      #imgrespage=curl_get(i)
      #imgdescription=re.findall("<p class=il_n>([^<]*)</p>",imgrespage)
      #out4.append("".join(imgdescription))
    #print
    
    #parallel version
    out4=[]
    imgresurls=[]
    from multiprocessing import Pool
    
    for i in out2:
      if len(out4)>=imgreses:
        break
      imgresurls.append(re.sub(r"&amp;","&", i))
    
    
    print ".",
    sys.stdout.flush()
    p = Pool(5)
    out4pages = (p.map(curl_get, imgresurls))
    print
    for i in out4pages:
      imgdescription=re.findall("<p class=il_n>([^<]*)</p>",i)
      out4.append("".join(imgdescription))
    
    
    #http://stackoverflow.com/questions/15524030/counting-words-in-python
    from collections import Counter
    
    alldescriptions =  ""
    for i in out4:
      alldescriptions += " " + i.lower() 
    
    descriptionwords=re.findall(r'\w+',alldescriptions,re.UNICODE)
    descriptionbigrams=[]
    for i in range(len(descriptionwords)-1):
      descriptionbigrams.append(descriptionwords[i]+ " " + descriptionwords[i+1])
    
    out5=Counter(descriptionwords).most_common(10)
    out6=Counter(descriptionbigrams).most_common(10)
       
    return out,out5,out6



def main(argv):
    import argparse
    parser = argparse.ArgumentParser(description='Take Pictures and ask Google to name them')
    parser.add_argument('-s', '--snap', action='store_true', help='take a snapshot')
    parser.add_argument('-c', '--cam', nargs='?', type=int, help='use cam Number N defaults to 0', default=0)
    parser.add_argument('NAME', nargs='?', help='Filename defaults to snap.jpg', default="snap.jpg")
    cmdline_args = parser.parse_args(sys.argv[1:]) #cut the program-name off the list 
    
    #print  cmdline_args
    
    picture_file=cmdline_args.NAME
    
    if cmdline_args.snap:
      snapshot(picture_file,cmdline_args.cam)
      #snapshot(picture_file,0)
    
    if not os.path.exists(picture_file):
      print "missing " + picture_file + " you may want to capture it using -s (-h for Help)"
      sys.exit(-1)
        
    imgbuff = open(picture_file)
    img=imgbuff.read()
    ret = nameit(picture)
    
    for j in ret:
      for i in j:
        print i
      print "################################################################"

    

if __name__ == "__main__":
    sys.exit(main(sys.argv))