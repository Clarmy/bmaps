import urllib.request
import urllib.parse
import random
import time
import os
import requests
import logging
import json as js
from logging.handlers import TimedRotatingFileHandler

def setup_custom_logger(log_path,name,when):

    formatter = logging.Formatter(fmt='%(asctime)s:%(levelname)s:%(message)s')
    formatter.converter = time.gmtime
    handler = TimedRotatingFileHandler(log_path, utc=True,
                                       when='midnight')
    handler.suffix = '%Y%m%d.log'
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger

logger = setup_custom_logger('./bmap', 'root', when='midnight')


def get_count(zoom):
    if zoom == 1:
        return 3
    else:
        return 2*get_count(zoom-1)-1


def get_urls():
    url_dict = {}
    for z in range(1,9):
        url_dict[z] = []
        count = get_count(z)
        counts = range(count)
        for x in counts:
            for y in counts:
                url = 'https://aviationweather.gov/cgi-bin'\
                      '/tilecache/tc.php?product=globe_light'\
                      '&x={0}&y={1}&z={2}'.format(x,y,z)
                url_dict[z].append(('%s_%s'%(x,y),url))
    return url_dict


def download_img(url,savepfn):
    r = requests.get(url,stream=True)
    with open(savepfn, 'wb') as fd:
        for chunk in r.iter_content():
            fd.write(chunk)
    return True


def check_dirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

def main():
    urls = get_urls()
    root_path = './data/'
    failed_urls = {7:[],8:[]}
    for z in [7,8]:
        z_path = root_path+str(z)+'/'
        check_dirs(z_path)
        for urltuple in urls[z]:
            index = urltuple[0]
            x,y = index.split('_')
            url = urltuple[1]
            fn = x + '.jpg'
            savepath = z_path+y+'/'
            check_dirs(savepath)
            savepfn = savepath+fn
            try:
                download_img(url,savepfn)
                print('z:%s y:%s x:%s finished'%(z,y,x))
                logger.info('z:%s y:%s x:%s finished',z,y,x)
                time.sleep(0.1)
            except:
                print('z:%s y:%s x:%s failed'%(z,y,x))
                logger.info('z:%s y:%s x:%s failed',z,y,x)
                failed_urls[z].append('%s_%s'%(x,y),url)
                continue

    with open('./failed.json','w') as f:
        js.dump(failed_urls,f)


if __name__ == '__main__':
    main()
