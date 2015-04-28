#!/usr/bin/python

import sys

stopwordfilter=True
#stopwordfilter=False

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

def sanatizegoogleurl(url):
    import re
    return re.sub(r"&amp;","&", url)

def imgresurlprocessor(url):
    import re
    page = curl_get(url)
    descriptions = re.findall("<p class=il_n>([^<]*)</p>",page)
    description = ''
    for i in descriptions:
      description += " " + i.lower()
    descriptionwords = re.findall(r'\w+',description,re.UNICODE)
    descriptionbigrams = []
    for i in range(len(descriptionwords)-1):
      descriptionbigrams.append(descriptionwords[i] +  " " + descriptionwords[i + 1])
    
    if stopwordfilter:
        from nltk.corpus import stopwords
        #stop_words = stopwords.words('english')
        stop_words = stopwords.words()
        pattern = r'\b|\b'.join(stop_words)
        pattern = r'\b' +pattern + r'\b'
        prog = re.compile(pattern, re.IGNORECASE)
        words = filter(lambda x: not prog.search(x), descriptionwords)
        bigrams = filter(lambda x: not prog.search(x), descriptionbigrams)
    else:
        words = descriptionwords
        bigrams = descriptionbigrams
    
    return description, words, bigrams

headers = {}
def header_function(header_line):
    # HTTP standard specifies that headers are encoded in iso-8859-1.
    # On Python 2, decoding step can be skipped.
    # On Python 3, decoding step is required.
    header_line = header_line.decode('iso-8859-1')

    # Header lines include the first status line (HTTP/1.x ...).
    # We are going to ignore all lines that don't have a colon in them.
    # This will botch headers that are split on multiple lines...
    if ':' not in header_line:
        return

    # Break the header line into header name and value.
    name, value = header_line.split(':', 1)

    # Remove whitespace that may be present.
    # Header lines include the trailing newline, and there may be whitespace
    # around the colon.
    name = name.strip()
    value = value.strip()

    # Header names are case insensitive.
    # Lowercase name here.
    name = name.lower()

    # Now we can actually record the header name and value.
    headers[name] = value  


def nameit(picture_buffer, hint=None):
    
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
    postdict=[("encoded_image", (pycurl.FORM_BUFFER, "picture", pycurl.FORM_BUFFERPTR, picture_buffer)),]
    
    curl.setopt(curl.URL,"https://www.google.com/searchbyimage/upload")
    curl.setopt(curl.WRITEFUNCTION, buffer.write)
    #Google is unsing a redirect page as reply 
    curl.setopt(curl.FOLLOWLOCATION, True)
    curl.setopt(curl.COOKIEJAR, "kekstopf")
    #Google does some filtering on the userangent (it does not like to be asked by CURL or just Mozilla/5.0)
    curl.setopt(curl.USERAGENT,'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.91 Safari/537.36')
    curl.setopt(curl.HTTPPOST,postdict)
    curl.setopt(curl.HEADERFUNCTION, header_function)
    curl.perform()
    curl.close()
    
    page = buffer.getvalue()
    print hint
    print headers
     
    if hint!= None:
        durl = headers['location']+'&'+urlencode([('q',hint)])
        print durl
        page=curl_get(durl)
        
    #export googles response (not the redirecht page)
    f = open("page.htm","w")
    f.write(page)
    f.close()
    
    
   
    
    #Regex for /search?q=neue+5+euro+schein& (which is the blue text link to search the image content @google)
    #<a class="_gUb" href="/search?q=neue+5+euro+schein&amp;sa=X&amp;ei=7GIdVfugMcGfsAHql4PYAg&amp;ved=0CB0QvQ4oAA" style="font-style:italic">neue 5 euro schein</a>
    
    #out=re.findall(r"\/search\?q=([^&]*)", page)
    out=re.findall(r"<a class=\"_gUb\" [^>]*>([^<]*)</a>", page)
    out1=re.findall(r"<h3 class=\"r\"><a href=\"([^\"]*)\"",page)
    out2=map(sanatizegoogleurl,re.findall(r'http[^\"]*imgres[^\"]*',page))
    out3=re.findall(r'title="(htt[^"]*)', page)
    
    #what would google tag this?
    if len(out)<1:
      out=[]
    else:
      out=out[0]
      out=re.split('\W+',out,re.UNICODE)
    
    imgreses=60
    if len(out2)<imgreses:
      #find the  similar pictures link and follow
      similarpicturesurl=re.search(r"\/search\?tbs=simg:[^\">]*",page).group(0)
      similarpicturesurl="https://www.google.com"+sanatizegoogleurl(similarpicturesurl)
      oldlen=len(out2)
      
      simpage=curl_get(similarpicturesurl)
      out2=map(sanatizegoogleurl,re.findall(r'http[^\"]*imgres[^\"]*',simpage))
      for i in range(1, 20):
        if not len(out2)>oldlen or len(out2) >= imgreses:
            break 
        oldlen=len(out2)
        simpage=curl_get(similarpicturesurl + "&ijn=" + str(i) + "&start=" + str(i*100))
        out2.extend(map(sanatizegoogleurl,re.findall(r'http[^\"]*imgres[^\"]*',simpage)))

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
    imgresurls=out2[0:imgreses]
    NThreads=5
    from multiprocessing import Pool
    print "processing",len(imgresurls), "URLs using",  NThreads, "Threads",
    sys.stdout.flush()
    p = Pool(NThreads)
    imgresurlsprocessed = p.map(imgresurlprocessor, imgresurls)
    print "done"
    descriptions=[]
    descriptionwords=[]
    descriptionbigrams=[]
    for i in imgresurlsprocessed:
      imgdescription, imgwords, imgbigrams = i
      descriptions.extend(imgdescription)
      descriptionwords.extend(imgwords)
      descriptionbigrams.extend(imgbigrams)
    
    
    
    #alldescriptions =  ""
    #for i in out4:
      #alldescriptions += " " + i.lower() 
    
    #descriptionwords=re.findall(r'\w+',alldescriptions,re.UNICODE)
    #descriptionbigrams=[]
    #for i in range(len(descriptionwords)-1):
      #descriptionbigrams.append(descriptionwords[i]+ " " + descriptionwords[i+1])
    
    #http://stackoverflow.com/questions/15524030/counting-words-in-python
    from collections import Counter
    out4=descriptions
    out5=Counter(descriptionwords).most_common(10)
    out6=Counter(descriptionbigrams).most_common(10)
       
    return out,out5,out6



def main(argv):
    import os
    import sys
    import argparse
    parser = argparse.ArgumentParser(description='Take Pictures and ask Google to name them')
    parser.add_argument('-s', '--snap', action='store_true', help='take a snapshot')
    parser.add_argument('-c', '--cam', nargs='?', type=int, help='use cam Number N defaults to 0', default=0)
    parser.add_argument('-a', '--hint', nargs='?', type=str, help='use cam Number N defaults to 0', default=None)
    parser.add_argument('NAME', nargs='?', help='Filename defaults to snap.jpg', default="snap.jpg")
    
    cmdline_args = parser.parse_args(sys.argv[1:]) #cut the program-name off the list 
    
    picture_file=cmdline_args.NAME
    hint = cmdline_args.hint
    
    if cmdline_args.snap:
      snapshot(picture_file,cmdline_args.cam)
    
    if not os.path.exists(picture_file):
      print "missing " + picture_file + " you may want to capture it using -s (-h for Help)"
      sys.exit(-1)
        
    image_file = open(picture_file,'r')
    image_buffer=image_file.read()
    ret = nameit(image_buffer,hint)
    image_file.close()
    for j in ret:
      for i in j:
        print i
      print "" , len(j),  "################################################################"

    

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))