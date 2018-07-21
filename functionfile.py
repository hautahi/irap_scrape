from bs4 import BeautifulSoup as bs
import requests
from urlparse import urlparse
import pandas as pd
import urllib, re
import time

# -------------------
# 0. Define Functions
# -------------------

def make_soup(url):
    
    try:
        res = requests.get(url, timeout=5)
        soup = bs(res.text, "html.parser")
    except Exception:
        soup = []
    
    return(soup)

def get_externallinks(soup):
    
    links = []
    
    # Get the external references section
    exlinks = soup.find(id="External_links")
    if exlinks != None:
        exlinks = exlinks.find_next('ul')
        exlinks = exlinks.find_all("a",{'class':'external text'})

        # Extract links and store in list      
        for link in exlinks:
            x = urlparse(link.get("href", ""))
            if ("linked" in x[1]) | ("facebook" in x[1]):
                links.append(link.get("href", ""))
            else:
                links.append(x[0]+"://"+x[1])
    
    links = list(set(links))
    
    return(links)

def get_seealsos(soup):
    
    # Get the "see also" references section
    seealsos = []
    seealso_links = soup.find(id="See_also")
    
    if seealso_links != None:
        seealso_links = seealso_links.find_next('ul')
        seealso_links = seealso_links.find_all("a")
  
        for link in seealso_links:
            url = link.get("href", "")
            orgname = link.text

            if "/wiki" in url and ":" not in url:
                seealsos.append("https://en.wikipedia.org" + url)
    
    return(seealsos)
