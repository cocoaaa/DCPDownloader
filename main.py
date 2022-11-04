#!/usr/bin/env python
# coding: utf-8
import os,sys
from IPython.core.debugger import set_trace as breakpoint
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from pathlib import Path
from typing import Any,List, Set, Dict, Tuple, Optional, Iterable, Mapping, Union, Callable, TypeVar

# import for webcrawling
import bs4
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse
import requests

# ## Set Path 
ROOT = Path(os.getcwd())
SRC = ROOT/'src'
paths2add = [ROOT]

print("Project root: ", str(ROOT))
print('Src folder: ', str(SRC))

for p in paths2add:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
        print(f"\n{str(p)} added to the path.")
# print(sys.path)
# now can use modules in `src` folder
from src.report import DCPReport, is_valid_img_tag


# ## Helpers
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    """src:https://www.peterbe.com/plog/best-practice-with-retries-with-requests
    """
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def parse_lat_lng(soup: bs4.BeautifulSoup) -> Dict[str, Union[int, bool]]:
    """Parse the html of visit report to extract lat and lng"""
    
    meta_tags = soup.head.find_all('meta')
    
    lat, lng = None, None
    for meta_tag in meta_tags:
        attr_name = meta_tag.attrs.get('name')
        if attr_name is None:
            continue
        if attr_name == 'latitude':
            lat = meta_tag.attrs.get('content')
        if attr_name == 'longitude':
            lng = meta_tag.attrs.get('content')
   
    visit_idx = parse_visit_idx(soup)
    
    return {'lat': lat, 
            'lng': lng, 
            'visited': not lat is None, 
            'visit_idx': visit_idx}


def parse_visit_idx(soup: bs4.BeautifulSoup) -> int:
    
    try:
        title_str = soup.head.title.contents[0]
        # 'DCP (visit #3)'
        pos = title_str.find('#') + 1
        return title_str[pos]
    except:
        return -1
    


def download_visits(start_vid:int = 0, end_vid: int=22980, out_dir: Optional[str]=None,
                    print_every:Optional[int]=500)-> None:
    """Download all images from the first visit (id=0) to the latest (visit_id=22980)"""
    out_dir = out_dir or './outs'
    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True)

    # visit_ids = range(0,22981)
    visit_ids = range(start_vid, end_vid)

    for i, vid in enumerate(visit_ids):
        if (i+1) % print_every == 0:
            print(i+1, end='...', flush=True)
        try:
            report = DCPReport(vid)
            report.download_imgs(out_dir, filter_func=is_valid_img_tag)
        
        except:
            continue


if __name__ == '__main__':
    print('Start downloading ...')
    # test with visits from 0 to 10 (inclusive). save to outs dir (will be created if not existing)
    download_visits(0,10, out_dir='./outs')

    # download images from  all visits and save to `./outs` folder
    # download_visits(out_dir='./outs')
    print('Finished downloading!')
