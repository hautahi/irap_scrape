"""
This program manually changes the dataset produced programatically in previous files.
"""

import pandas as pd
import time

print("Manually adjusting results...")
start = time.time()

# Read in data of scraped candidates
df = pd.read_csv("./output/preliminary_scraped_candidates.csv")

# ------------------------------
# Manually exclude candidates based on exact websites
# ------------------------------

# Extract the scraped webpage information to a list
STR = df["Candidate Organization Link"].tolist()

# Pages to exclude
excl = ["http://www.horsetalk.co.nz","https://www.youtube.com","http://online.lewisu.edu","http://www.britishfashioncouncil.com", "http://www.tim.hawaii.edu","http://www.stern.nyu.edu","http://bmj.bmjjournals.com","http://law.jrank.org"]

# Filter datafame based on excluded websites above
exclude = [False if x in excl else True for x in STR]
df["exclude"] = exclude
d = df.loc[df['exclude'] == True]

# ------------------------------
# Manually exclude candidates based on presence of strings
# ------------------------------

# Extract the scraped webpage information to a list
STR = d["Candidate Organization Link"].tolist()

# Filter based on existence of some string
excstrings = [".org.uk",".gov",".co.uk",".org.au"]

exclude1 = []
for str1 in STR:
    if any(s in str1 for s in excstrings):
        exclude1.append(True)
    else:
        exclude1.append(False)

# Filter datafame based on excluded websites above
d["exclude1"] = exclude1
d = d.loc[d['exclude1'] == True]

# Tidy up
d = d[['Candidate Organization Link','Industry','Industry Group Description','Candidate Organization Name','Contact Information']]

# ------------------------------
# Include Manually-identified candidates
# ------------------------------

# Read in data of scraped candidates
man = pd.read_csv("manual_additions.csv")

# Extract Relevant Information
df2 = man[['Candidate Organization Link','Industry']]
df2['Industry Group Description'] = ""
df2['Candidate Organization Name'] = man[['organization']]
df2['Contact Information'] = ""

# Combine
d = d.append(df2, ignore_index=True)

# Save
d.to_csv("./output/scraped_candidates.csv",index=False,encoding='utf-8')

print("%s seconds" %(time.time()-start))




