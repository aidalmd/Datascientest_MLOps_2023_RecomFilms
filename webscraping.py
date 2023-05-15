from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from bs4 import UnicodeDammit 
import pandas as pd

from config import URL

site_url = URL
page = urlopen(site_url)
soup = bs(page, "html.parser")

