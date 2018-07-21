"""
This program extracts some organization links from a word file, visits those links and saves their link texts.
"""

import pandas as pd
import docxpy
from functionfile import make_soup
import time

start = time.time()

# extract text from word file
file = 'Potential Certifiers - Advanced Manufacturing.docx'
doc = docxpy.DOCReader(file)
doc.process()
hyperlinks = doc.data['links']

# Extract Links from word doc
orgs = [x[0] for x in hyperlinks]
links = [x[1] for x in hyperlinks]

# Visit Webpages and extract relevant text
STR = []
for site in links:
    
    # Grab website
    soup = make_soup(site)

    if soup != []:
               
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
        bigstring = []
        
    # Add to list
    STR.append(bigstring)
    
# Save to dataframe
d = {'Organization Name': orgs, "Candidate Front Page Info":STR,
    'Candidate Organization Link': links}
df = pd.DataFrame(d)

# Save as csv
df.to_csv("./output/worddocorgs_tosearch.csv",index=False,encoding='utf-8')


print("%s seconds" %(time.time()-start))




