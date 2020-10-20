# Working script to download from url
import requests
import datetime
from time import sleep

def main():
    urls = ['http://americanmotocrosslive.com/xml/mx/racelaptimes.xml', 
        'http://americanmotocrosslive.com/xml/mx/raceresultsweb.xml',
        'http://americanmotocrosslive.com/xml/mx/raceresults.json',
        'http://americanmotocrosslive.com/xml/mx/racelaptimes.json']
    
    n = 0
    while (True):
        now = datetime.datetime.now().hour
        if now >= 10 and now <= 20:
            download(urls)
            n += 1
            print(n,'-', datetime.datetime.now())
            sleep(60)
        else: print('Will start later')
        sleep(360)
        

def download(urls):
    for url in urls:
        time = str(datetime.datetime.now()).rsplit('.',1)[0].replace(':','').replace('-','')
        filename = (r"C:\Users\orlow\Google Drive\Computing\MotoAnalysis\resultsdownloads\09 Pala" + time + ' ' + url.rsplit('/', 1)[1])
        site = requests.get(url)
        open(filename, 'wb').write(site.content)
        print(filename, 'downloaded')


main()