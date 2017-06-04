#!/usr/bin/env python
import requests
import csv
import re
from bs4 import BeautifulSoup
from operator import itemgetter

BASE_URL = "https://portforward.com/router-password/"
PASSWORD_CSV = "passwords.csv"

def dump_maker_page(url):
    r = requests.get(BASE_URL + url)
    soup = BeautifulSoup(r.text, "html.parser")

    # Find the table
    table = soup.find("table", attrs={"class": "dptable"})
    if not table:
        return None

    # Get maker from table title
    maker = table.find("tr")
    if not maker:
        return None

    maker = maker.string

    # Get credentials from table
    creds = []
    for tr in table.find_all("tr")[2:]:
        td = tr.find_all("td")
        if not td:
            continue

        # For whatever reason the username and password strings contain an \xa0
        # character, so we trim it with [:-1]
        creds.append([maker, td[0].string, td[1].string[:-1], td[2].string[:-1], ""])

    return creds

def dump_passwords():
    r = requests.get(BASE_URL)
    soup = BeautifulSoup(r.text, "html.parser")

    # Find the div that holds the data
    holder_div = soup.find("div", attrs={"id": "double_column_data"})
    if not holder_div:
        return None

    # From here, the only hrefs should be router pages, so we can just hunt
    # for a's under that assumption
    creds = []
    for a in holder_div.find_all("a"):
        # Find the link, if it exists.  Note the regex hack to eliminate the
        # useless #<letter> links!
        href = a.get("href")
        if href and not re.search("^#.*$", href):
            print("Dumping \"{}\" ... ".format(href), end="")
            c = dump_maker_page(href)
            if c:
                creds += c
                print("Done")
            else:
                print("Failed")

    return creds

def main():
    passwords = dump_passwords()
    if not passwords:
        return

    with open(PASSWORD_CSV, "r") as f:
        data = [line for line in csv.reader(f)]

    data += passwords
    data.sort(key=itemgetter(0))
    data = ["Manufacturer", "Model", "Username", "Password", "Notes"] + data

    with open(PASSWORD_CSV, "w") as f:
        csv.writer(f).writerows(data)

if __name__ == "__main__":
    main()
