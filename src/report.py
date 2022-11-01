import os,sys
from pathlib import Path
from typing import Any,List, Set, Dict, Tuple, Optional, Iterable, Mapping, Union, Callable, TypeVar
from tqdm import tqdm

# import for webcrawling
import bs4
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from IPython.core.debugger import set_trace as breakpoint

class DCPParser:
    pass

class DCPReport:
    
    # def __init__(self, lat: int, lng:int):
    def __init__(self, vid:int):

        """
        lat: goes from -180(south) to 180(north), 
        lng: from -180 (west), to 180 (east)
        """
        self.vid = vid
        # self.report_url = f'https://confluence.org/confluence.php?lat={lat}&lon={lng}'
        self.report_url = f'https://confluence.org/confluence.php?visitid={vid}'
        self.img_page_url = f'https://confluence.org/photo.php?visitid={vid}&pic=ALL'
        self.was_visited = None
        self.lat = None
        self.lng = None
        self.visit_idx = None
        self.img_urls = []
        self.text = ''
        self.year = None
        self.country = ''
        
        self.update_metadata()

    def info(self):
        print('vid: ', self.vid)
        print('was visited: ', self.was_visited)
        print('lat: ', self.lat)
        print('lng: ', self.lng)
        print
        print('visit_idx: ', self.visit_idx)
        print('text: ', self.text)
        
        
    def update_metadata(self) -> None:
        """Parse html to get last,lng,text descr, year,country,
        and set the properties to the parsed values"""
        # get hrml content of url
        r = requests_retry_session().get(self.report_url)
        soup = bs4.BeautifulSoup(r.text, 'html.parser')

        # parse html 
        d_meta = DCPReport.parse_lat_lng(soup)
        self.lat, self.lng = d_meta.get('lat'), d_meta.get('lng')
        self.was_visited = self.lat is not None
        
        if self.was_visited:
            self.visit_idx = DCPReport.parse_visit_idx(soup)    
            self.text = DCPReport.parse_report_text(soup)
            # self.year = 
            # self.country = 
    

    def download_imgs(self,
                  out_dir: Path,
                 filter_func: Optional[Callable]=None, 
                 verbose: bool=False) -> None:
        """Effect: sets self.img_urls, download image to out_dir.
        Each image is saved in the out_dir folder using the filename convention: 
        f'{vid}_{lat}_{lon}_{direction or img_alt}.jpg'
        
        
        Args
        ----
        out_dir : (Path) path to the directory to save the downloaded images
        filter_func : (Callable) it takes arguments of img_url (str) and img_alt (str), 
            and returns True if the Tag passes all conditions as a valid img tag.
            Otherwise, returns False.
            
        """
        if not self.was_visited:
            print(f'{self.vid} has not been visited. Pass.')
            return
            
        # get hrml content of url
        r = requests_retry_session().get(self.img_page_url)
        # parse html 
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        
        img_tags = soup.find_all("img")

        # img_urls = [] 
        for img_tag in img_tags:
            img_alt = img_tag.attrs.get("alt")
            img_url = img_tag.attrs.get("src")
            if not img_url:
                continue

            # concat to get full address to the image
            img_url = urljoin(self.img_page_url, img_url)
            # remove error-prone http get kvey-values in the url
            try:
                pos = img_url.index("?")
                img_url = img_url[:pos]
            except ValueError:
                pass

            # check if img_url is valid according to conditions in filter_func
            if filter_func is not None and not filter_func(img_url, img_alt):
                # print(f'{img_url} does not pass the filter function') #todo: write to a log file
                # breakpoint()
                continue

            # download img_url
            suffix = Path(img_url).suffix
            # use filename convention: {vid}-{lat}-{lon}-{direction}.jpg'
            filename = self.create_filename(img_alt, suffix) 
            # print('Downlaoding: ', img_url)
            try:
                download(img_url, out_dir, filename)
            except:
                print(f'Download failed. Passing this url: {img_url}...')

            # collect all img_urls
            self.img_urls.append(img_url)
            if verbose:
                print(f'\n {img_url}')

        print(f'Done: downloaded {len(self.img_urls)} imgs for visit_id {self.vid}...')

    
    def create_filename(self, img_alt: str, suffix: str) -> str:
        img_alt = img_alt.lower().replace(' ', '-')
        return f'{self.vid}_{self.lat}_{self.lng}_{img_alt}{suffix}' 
        
        

    @staticmethod
    def parse_visit_idx(soup: bs4.BeautifulSoup) -> int:
        
        try:
            title_str = soup.head.title.contents[0]
            # 'DCP (visit #3)'
            pos = title_str.find('#') + 1
            return title_str[pos]
        except:
            return -1

    @staticmethod
    def parse_lat_lng(soup: bs4.BeautifulSoup) -> Dict[str, Union[int, bool]]:
        
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
    
        
        return {'lat': lat, 
                'lng': lng}
        
    @staticmethod
    def parse_report_text(soup) -> str:
        table_tags = soup.body.table.find_all('table')
        descr_table = table_tags[-1]
        
        text = ''
        for para_str in descr_table.div.stripped_strings:
            text += para_str
        return text









        
################################################################################
#  Helpers
################################################################################
def requests_retry_session(
    retries=10,
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

def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

# define a valid img_tag
def is_valid_img_tag(img_url: str, img_alt: str) -> bool:
    
    # conditions to meet
    meets_cond1 = is_valid(img_url)
    meets_cond2 = '.gif' not in img_url.lower()
    meets_cond3 = 'gps' not in img_alt.lower()
    
    # debug
    # print('cond1: ', meets_cond1)
    # print('cond2 ', meets_cond2)
    # print('cond3: ', meets_cond3)
 
    return meets_cond1 and meets_cond2 and meets_cond3


def download(url: str, dirpath: Path, out_bn: Optional[str]=None):
    """Downloads a file given an URL and puts it in the folder `pathname`
    """
    # if path doesn't exist, make that path dir
    if not dirpath.exists():
        dirpath.mkdir(parents=True)
        print('Created: ', dirpath)
        
    # download the body of response by chunk, not immediately
    response = requests.get(url, stream=True)
    # get the file name
    out_bn = out_bn or  url.split("/")[-1]
    out_fn = dirpath / out_bn
    
    
    
    # Alt: show with tqdm progress bar
    # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
    # progress = tqdm(response.iter_content(1024), 
    #                 f"Downloading {out_fn}", total=file_size, unit="B", 
    #                 unit_scale=True, unit_divisor=1024)
    if not response.status_code == 200:
        return 
    
    with open(out_fn, "wb") as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)