"""
This program scrapes see also and external links based on a collection of some "source" Wikipedia pages.

@author: hautahi
"""

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

# -------------------
# 1. Get information from Wikipedia route sources
# -------------------

print("Extracting Information from Source Pages...")
start = time.time()

# Grab page and soupify main source
soup = make_soup("https://en.wikipedia.org/wiki/List_of_industry_trade_groups_in_the_United_States")

# Get a list of soups of all h3 headings
section_headings = soup.findAll('h3')            

# Get list of 16 industry headings
industry = []
for s in section_headings:
    x = s.find('span', attrs={'class':'mw-headline'})
    if x != None:
        industry.append(x.text)

# Get a list of soups (one for each of 16 sections)
sections = soup.findAll('div', attrs={'class':'div-col columns column-width'})

# Collect list of links to the individual wiki pages
wikipages,industries, organization = [], [], []
for ind, section in zip(industry,sections):
    for link in section.find_all("a"):
        url = link.get("href", "")
        orgname = link.text
        if "/wiki" in url and ":" not in url:
            wikipages.append(url)
            industries.append(ind)
            organization.append(orgname)

# Add baseurl to all the links
baseurl = "https://en.wikipedia.org"
wikilinks = [baseurl + x for x in wikipages]

# Now manually add pages provided by subject matter experts
man = pd.read_csv("manual_additions.csv")

wikilinks = wikilinks + man["wikipage"].tolist()
industries = industries + man["industry"].tolist()
organization = organization + man["organization"].tolist()

print("%s seconds" %(time.time()-start))

# -------------------
# 2. Visit each wikipedia page and extract the external links and "see also" wiki links
# -------------------

print("Extracting Information from Wikipedia Pages...")
start = time.time()

# Visit each page, get external links and wiki pages for those in the "see also" sections
# Note: We're using append so we can attach the industry and organization later
org_names,links,seealsos,desc = [],[],[],[]
for link in wikilinks:
    soup = make_soup(link)
    links.append(get_externallinks(soup))
    seealsos.append(get_seealsos(soup))
    desc.append(soup.find("p").text)

# Visit the "see also" wiki pages and get the external links
links1, desc1, ind1 = [], [], []
for i,l in enumerate(seealsos):
    for link in l:
        soup = make_soup(link)
        ind1.append(industries[i]) 
        links1.append(get_externallinks(soup))
        desc1.append(soup.find("p").text)

# Filter out some external links
excludes = ["facebook","linkedin","archive"]
filtered_links = []
for l in links:
    filtered_links.append(filter(lambda x: not any(ext in x for ext in excludes),l))

filtered_links1 = []
for l in links1:
    filtered_links1.append(filter(lambda x: not any(ext in x for ext in excludes),l))

# Expand the list of lists and gather into dataframe
IND, WIKI, ORG, F, D = [], [], [], [], []
for i, f in enumerate(filtered_links):
    for x in f:
        IND.append(industries[i])
        WIKI.append(wikilinks[i])
        #ORG.append(organization[i])
        D.append(desc[i])
        F.append(x)

flat_seealsos = [item for sublist in seealsos for item in sublist]
for i, f in enumerate(filtered_links1):
    for x in f:
        IND.append(ind1[i])
        WIKI.append(flat_seealsos[i])
        #ORG.append(organization[i])
        D.append(desc1[i])
        F.append(x)

d = {'Industry': IND, "Industry Group Description":D,
     'Industry Group Wiki Page': WIKI,'Candidate Organization Link': F}
df = pd.DataFrame(d)

# Filter out http/https double-ups
F = df['Candidate Organization Link'].tolist()

# Strip the start
o = []
for link in F:
    o.append(urlparse(link).netloc)
    
# Find duplicates
duplicate, seen = [], set()
for x in o:
    if x not in seen:
        duplicate.append(False)
        seen.add(x)
    else:
        duplicate.append(True)

df["duplicate"] = duplicate
df = df.loc[df['duplicate'] == False]
df = df.reset_index(drop=True)

# Save as csv
df.to_csv("./output/candidate_organizations.csv",index=False,encoding='utf-8')

print("%s seconds" %(time.time()-start))
