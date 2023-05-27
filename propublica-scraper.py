from requests.models import LocationParseError
import requests
from bs4 import BeautifulSoup
import csv
#from google.colab import files
import re
import time
import random
import os

def getinfo(soup):

    #NAME OF ORGANIZATION
    content = soup.find("div", {"class": "left-col"})
    if(content == None):
        return ["N/A", "N/A", "N/A", "No"]
    orgname = content.find("h1").text.strip()
    if(orgname == "Unknown Organization"):
        return ["N/A", "N/A", "N/A", "No"]

    ein = "N/A"
    classification = "N/A"
    taxcode = "No"

    #GATHERING INFO
    info = content.find("div", {"class": "profile-info"})
    informationli = info.find_all("li")

    #Going through "li" list of information
    for information in informationli:
        if("EIN" in information.text):
            ein = information.text.strip()
            ein = ein.split(" ")[1]
        elif("Classification" in information.text):
            classification = information.text.strip().split("(NTEE)")[1].strip()
            classification = re.sub(r'\n', '', classification)
            classification = re.sub(r'\s+', ' ', classification)
        elif("501(c)(3)" in information.text):
            taxcode = "Yes"


    return([orgname, ein, classification, taxcode])

def getfinancials(revenues_container):

    # Iterate over each revenue container, skipping the header row
    for revenue_container in revenues_container.find_all("div", {"class": "single-filing"}):

        yearloc = revenue_container.find("h4", {"class": "year-label"})

        year = "N/A"
        revenue = "N/A"
        expenses = "N/A"
        income = "N/A"

        if(yearloc != None):
            year = yearloc.text.strip()
            year = year.split(" ")[1]
            revenue_table = revenue_container.find("table", {"class": "revenue"})

            #write revenue, expenses, income data if exists, else continue
            if(revenue_table!=None):

                pos = revenue_table.find("th", {"class": "pos"})
                if(pos != None):
                    revenueloc = pos.find("h3")
                    if(revenueloc== None):
                        revenue = "N/A"
                    else:
                        revenue = revenueloc.text.strip().replace("$", "").replace(",", "")
                else:
                    revenue == "N/A"

                expensesloc = revenue_table.find("th", {"class": "neg"})
                if(expensesloc == None):
                    expenses = "N/A"
                else:
                    expenses = expensesloc.text.strip().replace("$", "").replace(",", "")

                incomeloc = revenue_table.find("th", {"class": "tablenum pos"})
                if(incomeloc == None):
                    income = "N/A"
                else:
                    income = incomeloc.text.strip().replace("$", "").replace(",", "")

            #if any financial data is filled out, break and write
            if(revenue != "N/A" or expenses != "N/A" or income != "N/A"):
                break
            
    return([year, revenue, expenses, income])

def process_txt_file(file_path):
    txt_file_name = os.path.basename(file_path)
    txt_file_id = re.findall(r'\d+', txt_file_name)[0]
    csv_file_name = "revenues_split_" + txt_file_id + ".csv"
    csv_file_path = os.path.join('revenues', csv_file_name)

    csv_exists = os.path.isfile(csv_file_path)

    csv_file = open(csv_file_path, "a", newline="")
    writer = csv.writer(csv_file)

    # Write the header row only if the file doesn't exist or is empty
    if not csv_exists or os.path.getsize(csv_file_path) == 0:
        writer.writerow(["Name of Organization", "EIN", "Classification", "Nonprofit Tax Code Designation: 501(c)(3)",
                         "FISCAL YEAR", "Total Revenue", "Total Functional Expenses", "Net Income"])

    print(csv_file_path)

    existing_ids = set()
    if csv_exists:
        with open(csv_file_path, "r", newline="") as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Skip the header row
            for row in reader:
                if(len(row)>1):
                    existing_ids.add(row[1].replace("-", ""))  # Assuming EIN is in the second column

    print(existing_ids)

    count = 0
    scrapped = 0

    urlformat = "https://projects.propublica.org/nonprofits/organizations/"

    with open(file_path, "r") as orgstxt:
        for line in orgstxt:
            id = line.split("|")[0]

            if id in existing_ids:
                print("skipping")
                continue  # Skip to the next ID
            print("not skipping")

            url = urlformat + id
            count += 1

            # Send a GET request to the URL
            response = requests.get(url)
            if response.status_code != 200:
                print(response.status_code, url)
                if response.status_code == 403:
                    break
                continue
            scrapped += 1

            # Parse the HTML content of the page with Beautiful Soup
            soup = BeautifulSoup(response.content, "lxml")

            # Find the div with all revenues
            revenues_container = soup.find("div", {"class": "filings"})
            if revenues_container is None:
                continue

            # Create a CSV file to write the data to

            info = getinfo(soup)
            if info[0] == "Unknown Organization" or info[0] == "N/A":
                continue

            financials = getfinancials(revenues_container)

            total = info + financials

            #print(total)
            writer.writerow(total)

            time.sleep(random.randint(3, 5))

    csv_file.close()


def process_split_files():
    folder_path = 'split-files'
    for file_name in os.listdir(folder_path):
        if file_name.startswith('propublica_split_') and file_name.endswith('.txt'):
            file_path = os.path.join(folder_path, file_name)
            process_txt_file(file_path)

process_split_files()

#download csv file
#print(count)
#print(scrapped)
#orgstxt.close()
#csv_file.close()
#files.download("revenues.csv")
