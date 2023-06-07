import requests
from bs4 import BeautifulSoup
import csv
import re
import time
import random
import os

def getinfo(soup):
    """
    Extracts organization information from the soup object.

    Args:
        soup (BeautifulSoup): Soup object of the web page.

    Returns:
        list: List containing organization information.
    """

    content = soup.find("div", {"class": "left-col"})
    if content is None:
        return ["N/A", "N/A", "N/A", "No"]
    orgname = content.find("h1").text.strip()
    if orgname == "Unknown Organization":
        return ["N/A", "N/A", "N/A", "No"]

    ein = "N/A"
    classification = "N/A"
    taxcode = "No"

    info = content.find("div", {"class": "profile-info"})
    informationli = info.find_all("li")

    for information in informationli:
        if "EIN" in information.text:
            ein = information.text.strip().split(" ")[1]
        elif "Classification" in information.text:
            classification = information.text.strip().split("(NTEE)")[1].strip()
            classification = re.sub(r'\n', '', classification)
            classification = re.sub(r'\s+', ' ', classification)
        elif "501(c)(3)" in information.text:
            taxcode = "Yes"

    return [orgname, ein, classification, taxcode]

def getfinancials(revenues_container):
    """
    Extracts financial information from the revenues container.

    Args:
        revenues_container (BeautifulSoup): Revenues container object.

    Returns:
        list: List containing financial information.
    """

    for revenue_container in revenues_container.find_all("div", {"class": "single-filing"}):

        yearloc = revenue_container.find("h4", {"class": "year-label"})

        year = "N/A"
        revenue = "N/A"
        expenses = "N/A"
        income = "N/A"

        if yearloc is not None:
            year = yearloc.text.strip().split(" ")[1]
            revenue_table = revenue_container.find("table", {"class": "revenue"})

            if revenue_table is not None:
                pos = revenue_table.find("th", {"class": "pos"})
                if pos is not None:
                    revenueloc = pos.find("h3")
                    if revenueloc is not None:
                        revenue = revenueloc.text.strip().replace("$", "").replace(",", "")
                else:
                    revenue = "N/A"

                expensesloc = revenue_table.find("th", {"class": "neg"})
                if expensesloc is not None:
                    expenses = expensesloc.text.strip().replace("$", "").replace(",", "")

                incomeloc = revenue_table.find("th", {"class": "tablenum pos"})
                if incomeloc is not None:
                    income = incomeloc.text.strip().replace("$", "").replace(",", "")

            if revenue != "N/A" or expenses != "N/A" or income != "N/A":
                break

    return [year, revenue, expenses, income]

def process_txt_file(file_path):
    """
    Processes a TXT file and extracts information to write to a CSV file.

    Args:
        file_path (str): Path to the TXT file.
    """

    txt_file_name = os.path.basename(file_path)
    txt_file_id = re.findall(r'\d+', txt_file_name)[-1]  # Extract the last number as ID
    csv_file_name = "revenues_split_" + txt_file_id + ".csv"
    csv_file_path = os.path.join('revenues', csv_file_name)
    print(csv_file_path)

    csv_exists = os.path.isfile(csv_file_path)

    csv_file = open(csv_file_path, "a", newline="")
    writer = csv.writer(csv_file)

    # Write the header row only if the file doesn't exist or is empty
    if not csv_exists or os.path.getsize(csv_file_path) == 0:
        writer.writerow(["Name of Organization", "EIN", "Classification", "Nonprofit Tax Code Designation: 501(c)(3)",
                         "FISCAL YEAR", "Total Revenue", "Total Functional Expenses", "Net Income"])

    existing_ids = set()
    if csv_exists:
        with open(csv_file_path, "r", newline="") as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Skip the header row
            for row in reader:
                if len(row) > 1:
                    existing_ids.add(row[1].replace("-", ""))  # Assuming EIN is in the second column

    count = 0
    scraped = 0

    urlformat = "https://projects.propublica.org/nonprofits/organizations/"

    with open(file_path, "r") as orgstxt:
        for line in orgstxt:
            id = line.split("|")[0]

            if id in existing_ids:
                continue  # Skip to the next ID

            url = urlformat + id
            count += 1

            response = requests.get(url)
            if response.status_code != 200:
                print(response.status_code, url)
                if response.status_code == 403:
                    break
                continue

            scraped += 1

            soup = BeautifulSoup(response.content, "lxml")

            revenues_container = soup.find("div", {"class": "filings"})
            if revenues_container is None:
                continue

            info = getinfo(soup)
            if info[0] == "Unknown Organization" or info[0] == "N/A":
                continue

            financials = getfinancials(revenues_container)

            total = info + financials
            writer.writerow(total)

            time.sleep(random.randint(3, 5))

    csv_file.close()

def main():
    """
    Processes all split TXT files in the folder and generates CSV files with the extracted information.
    """

    folder_path = 'split-files'
    if not os.path.exists('revenues'):
        os.makedirs('revenues')

    file_ids = []
    for file_name in os.listdir(folder_path):
        if file_name.startswith('propublica_split_') and file_name.endswith('.txt'):
            file_id = re.findall(r'\d+', file_name)[0]
            file_ids.append(int(file_id))

    file_ids.sort()  # Sort the file IDs in ascending order

    for file_id in file_ids:
        file_name = f"propublica_split_{file_id}.txt"
        file_path = os.path.join(folder_path, file_name)
        process_txt_file(file_path)
        

if __name__ == "__main__":
    main()
