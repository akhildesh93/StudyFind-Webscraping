This project runs on Google Cloud Platform's Compute Engine remotely.
Each webpage access has a delay of 3-5 seconds to prevent page blocking, so it must be ran remotely.
The GCP engine writes splitted csv files on 1,200,000+ pages of data.

propublica-scraper.py:
- processes txt files of propublica page id's
- allows for pausing and resuming 
- extracts financial data and classifications
- uses Python's BeautifulSoup library
- delays requests to prevent page blocking
- monitors for HTTP error status codes (eg. 404, 403)

shortlist.txt:
- a file containing the first 10000 out of 1.2 million page ids to scrape
- in the engine, the program is fed a folder of splitted txt files

revenues.csv:
- a showcase of the program's output
- in the engine, the program creates splitted revenues.csv files 

