This project runs on Google Cloud Platform's Compute Engine remotely.
Each webpage access has a delay of 3-5 seconds to prevent page blocking, so it must be ran remotely.
The GCP engine writes splitted csv files on 1,200,000+ pages of data.

propublica-scraper.py:
- processes txt files of propublica page id's
- allows for pausing and resuming of csv writing
- methods to extract financial data and classifications
- uses Python's BeautifulSoup library

shortlist.txt:
- a txt file containing the first 10000 out of 1.2 million page ids to scrape

revenues.csv:
- a showcase of the program's output

