"""
This program extracts information from the front page of the list of scraped candidates
"""

from bs4 import BeautifulSoup as bs
import requests
from urlparse import urlparse
import pandas as pd
import urllib, re
import time
from irap_scrape import make_soup

print("Extracting Information from Organization Websites...")
start = time.time()

# Read scraped candidate organizations
df = pd.read_csv("candidate_organizations.csv")

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
df["Candidate Front Page Info"] = STR    
df["Contact Information"] = CONTACT    
df.to_csv("./output/candidate_organizations_tosearch.csv",index=False,encoding='utf-8')

print("%s seconds" %(time.time()-start))
