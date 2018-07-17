"""
This program filters an initial list of scraped candidates based on the presence of keywords on their front webpage.
"""

import pandas as pd
import time

print("Filtering websites based on keywords...")
start = time.time()

# Read in data of scrapes candidates
df = pd.read_csv("candidate_organizations_tosearch.csv")

# Extract the scraped webpage information to a list
STR = df["Candidate Front Page Info"].tolist()

# Declare the keywords to be searched for
kw = ["apprentice","certification", "certificate", "workforce","talent","credential","skill","competency","training"]

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

# Filter datafame based on presence of keyword
df["relevant"] = relevant
d1 = df.loc[df['relevant'] == True]

# Clean up dataframe
d1 = d1.drop(columns=['Industry Group Wiki Page', 'duplicate','relevant'])

# Manually delete some entries


# Manually add some entries


# Save dataframe
d1.to_csv("preliminary_scraped_candidates.csv",index=False,encoding='utf-8')

print("%s seconds" %(time.time()-start))




