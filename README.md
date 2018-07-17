# irap_scrape

This repository contains the Python code and results of the IRAP web scraping exercise. File descriptions are as follows

- `1.irap_scrape` extracts a collection of organization websites using a variety of Wikipedia "source" pages. The results are saved in `output/candidate_organizations.csv`.

- `2.extract_webinfo.py` visits the websites gathered in the first step and extracts information from the front page. Results are saved in `output/candidate_organizations_tosearch.csv`.

- `3.filter.py` filters the list of scraped candidates based on the presence of keywords on the front page. Results are saved in  `output/preliminary_scraped_candidates.csv`.

- `4.manual_process.py` makes some manual adjustments to the dataset using information from `manual_additions.csv`. The final results are saved as `output/scraped_candidates.csv`.
