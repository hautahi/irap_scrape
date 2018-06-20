from bs4 import BeautifulSoup as bs
import requests
from urlparse import urlparse
import cPickle
import pandas as pd
import urllib, re

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

def get_externallinks(url):
    
    links = []
    
    # Grab page and soupify
    soup = make_soup(url)

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

# -------------------
# 1. Get information from the main wikipedia page
# -------------------

# Grab page and soupify
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
sections = soup.findAll('div', attrs={'class':'div-col columns column-count column-count-2'})

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

# -------------------
# 2. Get External Links
# -------------------

# Add baseurl to all the links
baseurl = "https://en.wikipedia.org"
wikilinks = [baseurl + x for x in wikipages]

# Visit each page and get external links
org_names,links,desc = [],[],[]
for link in wikilinks:
    links.append(get_externallinks(link))
    desc.append(make_soup(link).find("p").text)

# Filter out some external links
filtered_links = []
excludes = ["facebook","linkedin","archive"]
for l in links:
    filtered_links.append(filter(lambda x: not any(ext in x for ext in excludes),l))
    
# Save as pickled python files
cPickle.dump(industries,open("industries.p","w+"))
cPickle.dump(wikilinks,open("wiki_links.p","w+"))
cPickle.dump(filtered_links,open("external_links.p","w+"))
cPickle.dump(organization,open("organizations.p","w+"))
cPickle.dump(desc,open("descriptions.p","w+"))

# Gather expanded version into dataframe
IND, WIKI, ORG, F, D = [], [], [], [], []
for i, f in enumerate(filtered_links):
    for x in f:
        IND.append(industries[i])
        WIKI.append(wikilinks[i])
        ORG.append(organization[i])
        D.append(desc[i])
        F.append(x)

d = {'Industry': IND,'Industry Group': ORG, "Industry Group Description":D,
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
df.to_csv("candidate_organizations.csv",index=False,encoding='utf-8')

# -------------------
# 3. Visit each website and collect some information
# -------------------

TITLE, STR, CONTACT = [], [], []
for site in df['Candidate Organization Link'].tolist():
    
    # Grab website
    soup = make_soup(site)

    if soup != []:
        
        # Grab title
        title = soup.title
        if title != None:
            title = title.text.strip().replace("\n", "").replace("\r", "").strip()
        else:
            title = []

        # Grab contact information
        try:
            s = urllib.urlopen(site).read()
            phone = re.findall(r"\+\d{2}\s?0?\d{10}",s)
            email = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+.[A-Za-z]{2,4}",s)
            contact = phone + email
            contact = list(set(contact))
        except Exception:
            contact = []
               
        # Get the text of all links
        linksoups = soup.findAll('a')

        # Filter out some links
        newlinks = []
        for link in linksoups:
            if ("#" not in link.get("href", "")) & (len(link.text.strip())>0):
                newlinks.append(link)

        # Gather link texts
        linktexts = []
        for link in newlinks:
            linktexts.append(link.text.strip().replace("\n", " ").replace("\r", " "))
        linktexts = list(set(linktexts))

        bigstring = " ".join(linktexts)
    
    else:
        title, bigstring, contact = [], [], []
    
    # Add to list
    TITLE.append(title)
    STR.append(bigstring)
    CONTACT.append(contact)

# Add to csv and save
df["Candidate Organization Name"] = TITLE
df["Candidate Front Page Links"] = STR    
df["Contact Information"] = CONTACT    
df.to_csv("candidate_organizations_tosearch.csv",index=False,encoding='utf-8')

# -------------------
# 4. Search websites for keywords
# -------------------

STR = df["Candidate Front Page Links"].tolist()
kw = ["student","educat","certifi","learn","train"]

# Discover if website contains words from kw
relevant = []
for str1 in STR:
    if isinstance(str1, basestring):
        if any(s in str1.lower() for s in kw):
            relevant.append(True)
        else:
            relevant.append(False)
    else:
        relevant.append(False)
        
df["relevant"] = relevant
#df.to_csv("filtered.csv",index=False,encoding='utf-8')

# Create new dataframe based on condition
d1 = df.loc[df['relevant'] == True]
d1.to_csv("preliminary_scraped_candidates.csv",index=False,encoding='utf-8')
