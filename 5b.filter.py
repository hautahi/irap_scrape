"""
This program searches the text for the presence of keywords and indicates which keywords were matched.
"""

import pandas as pd
import time

print("Filtering websites based on keywords...")
start = time.time()

# Read in data of scrapes candidates
df = pd.read_csv("./output/worddocorgs_tosearch.csv")

# Extract the scraped webpage information to a list
STR = df["Candidate Front Page Info"].tolist()

# Declare the keywords to be searched for
kw = ["apprentice","certification", "certificate", "workforce","talent","credential","skill","competency","training"]

# Discover if website contains words from kw
relevant = []
for str1 in STR:
    if isinstance(str1, basestring):
        temp = [1 if x in str1.lower() else 0 for x in kw]
        relevant.append(temp + [sum(temp)])
    else:
        relevant.append([0 for x in kw]+[0])

# Gather into dataframe
d = pd.DataFrame(relevant)
d.columns = kw + ["Number of keyword matches"]

# Filter datafame based on presence of keyword
d1 = pd.concat([df, d], axis=1, join_axes=[df.index])

# Clean up dataframe
d1 = d1.drop(columns=['Candidate Front Page Info'])

d1 = d1.sort_values(by=["Number of keyword matches"],ascending=False)

# Save dataframe
d1.to_csv("./output/worddoc_candidates.csv",index=False,encoding='utf-8')

print("%s seconds" %(time.time()-start))
