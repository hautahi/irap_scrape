"""
This program manually changes the dataset produced programatically in previous files.
"""

import pandas as pd
import time

print("Manually adjusting results...")
start = time.time()

# ------------------------------
# Manually exclude candidates
# ------------------------------

# Read in data of scraped candidates
df = pd.read_csv("./output/preliminary_scraped_candidates.csv")

# Extract the scraped webpage information to a list
STR = df["Candidate Organization Link"].tolist()

# Pages to exclude
excl = ["http://www.horsetalk.co.nz","https://www.youtube.com","http://www.ausae.org.au",
"http://online.lewisu.edu","http://www.indymedia.org.uk","http://www.britishfashioncouncil.com",
"http://www.britishfashioncouncil.co.uk","http://www.tim.hawaii.edu","http://www.lsionline.co.uk",
"http://www.abtt.org.uk","http://www.bsria.co.uk","http://www.safelincs.co.uk",
"http://www.safelincs.co.uk","http://www.stern.nyu.edu","http://bmj.bmjjournals.com",
"http://www.abpi.org.uk","http://www.HIMAA2.org.au"]

# Filter datafame based on excluded websites above
exclude = [False if x in excl else True for x in STR]
df["exclude"] = exclude
d = df.loc[df['exclude'] == True]

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




