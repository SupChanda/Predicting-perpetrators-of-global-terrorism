import requests
import re
from bs4 import BeautifulSoup as BS
import csv

years = range(1970, 2020)

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

six_month_ranges = ["January-June", "July-December"]

def process_data(processable_data, year, month):
    """
        Adds contextual information to each row
    """
    for i in range(0, len(processable_data)):
        if year == 1984:
            location_and_details = processable_data[i][3]
            location, details = location_and_details.split(': ')
            processable_data[i] = [
                f"{processable_data[i][0]} {year}", #date
                "Unknown", #type
                processable_data[i][1], #dead
                processable_data[i][2], #injured
                location, #location
                details, #details
                processable_data[i][4]
            ]
        if month != None:
            # print(processable_data[i][0])
            processable_data[i][0] = f"{month} {processable_data[i][0]} {year}"
            # print(processable_data[i][0])
        else:
            processable_data[i][0] = f"{processable_data[i][0]} {year}"

        processable_data[i] = processable_data[i][0:7]

def filter_table(table):
    return table["class"] == ["wikitable", "sortable"] or table["class"] == ["wikitable"]

def scrape_page(url, year, month):
    """
        Takes a url and scrapes the page from wikipedia and extracts
        the table row processable_data
    """
    page = requests.get(url)
    dom = BS(page.text,'html5lib')
    tables = dom.findAll('table', attrs={ "class": "wikitable"})
    tables = list(filter(filter_table, tables))
    if len(tables) > 1:
        processed_data = []
        # print(len(tables))
        for i, table in enumerate(tables):
            rows = table.findAll('tr')
            new_processable_data = [[td.text.strip() for td in tr.findAll('td')] for tr in rows]
            new_processable_data = new_processable_data[1:len(new_processable_data)]
            # print(i)
            if month == "January-June" or month == None:
                process_data(new_processable_data, year, months[i])
            elif month != None:
                process_data(new_processable_data, year, months[i + 6])

            processed_data = processed_data + new_processable_data[1:len(new_processable_data)]
        return processed_data
    else:
        table = tables[0]
        rows = table.findAll('tr')
        processable_data = [[td.text.strip() for td in tr.findAll('td')] for tr in rows]
        processable_data =processable_data[1:len(processable_data)]
        process_data(processable_data, year, month)
        # remove the header row
        return processable_data

data = [["date", "type", "dead", "injured", "location", "details", "perpetrator"]]

for year in years:
    # years > than 2014 are separated in a page for each month
    if year == 2019:
        months = months[0:4]
    if year > 2014:
        for month in months:
            print(f"Processing: {month} {year}")
            data = data + scrape_page(f"https://en.wikipedia.org/wiki/List_of_terrorist_incidents_in_{month}_{year}", year, month)
    # years between 2010 and 2014 have a page for every 6 months of the year
    elif year > 2010:
        for month_range in six_month_ranges:
            print(f"Processing: {month_range} {year}")
            data = data + scrape_page(f"https://en.wikipedia.org/wiki/List_of_terrorist_incidents_in_{month_range}_{year}", year, month_range)
    else:
        print(f"Processing: {year}")
        data = data + scrape_page(f"https://en.wikipedia.org/wiki/List_of_terrorist_incidents_in_{year}", year, None)

#write the file
with open('global_terrorism.csv', 'w') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerows(data)

csvFile.close()
