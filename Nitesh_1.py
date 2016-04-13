# Initial imports
import requests
import re  # For String manipulation like removing special characters from string
import csv  # Write output to CSV file
import fileinput
import xlwt
from bs4 import BeautifulSoup, SoupStrainer

import bs4  # import main module

print "Beautiful Soup Version " + bs4.__version__


# code

def Open_listing(each_listing):
    html = each_listing  # you'll need to define this.
    r = requests.get(html)
    html = r.text
    # we start with getting the soup for each page.
    list_struct = BeautifulSoup(html, "html.parser")
    return list_struct


def fetch_AdInfo(ad_page):
    page_info = {}
    try:
        # Find Boat details
        for detail in ad_page.find_all('div', {'class': 'collapsible open'}):
            tables = detail.findChildren('table')
            Boat_Details_table = tables[0]
            rows = Boat_Details_table.findChildren(['tr'])
            for cell in rows:
                th_val = cell.findChildren('th')
                td_val = cell.findChildren('td')
                page_info[th_val[0].string] = td_val[0].string
    except:
        pass

    # find Sellers contact number
    temp = ad_page.find('div', {'class': 'contact'})
    try:
        if temp is None:
             page_info['Seller_Contact'] = "0"
        else:
            try:
                for contact in ad_page.find_all('div', {'class': 'contact'}):
                    page_info['Seller_Contact'] = re.sub('\W+', '',contact.string)  # remove special characters from contact number and store in the page_info list
            except:
                pass
    except:
        pass
    # Find ZIPCODE of the Boat Location
    temp = ad_page.find('span', {'class': 'postal-code'})
    try:
        if temp is None:
            page_info['ZipCode'] = "0"
        else:
            for zipcode in ad_page.find_all('span', {'class': 'postal-code'}):
                page_info['ZipCode'] = zipcode.string
    except:
        pass

    # Find Price of the Boat
    temp= ad_page.find_all('span', {'class': 'bd-price contact-toggle'})
    try:
        if temp is None:
            page_info['Price'] = "0"
        else:
            for price in ad_page.find_all('span', {'class': 'bd-price contact-toggle'}):
                page_info['Price'] = re.sub('\W+', '', price.string)  # removes '$' ','  and spaces
    except:
        pass

    return page_info


# Write Ad information to excel
def write_to_excel(details, flag):
    inputFileName = "F:\PythonFiles\FinalProject\TestCsv.csv"
    len_of_details = details.__len__()
    for key, value in details.iteritems():
        temp = {}
        temp = value[0]
        with open(inputFileName, "ab") as f:
            w = csv.writer(f)
            if flag == 0:
                wh = csv.DictWriter(f, temp.keys())
                wh.writeheader()
                w.writerow(temp.values())
                flag = 1
            else:
                w.writerow(temp.values())
    return flag


# Finds total number of pages and listings per page returned by the search results
def find_search_results_details(raw_html):
    r = requests.get(raw_html)
    raw_html = r.text
    lastpage_struct = BeautifulSoup(raw_html, "html.parser")
    for lastpage in lastpage_struct.find_all('a', {'class': 'last'}, href=True):
        href = lastpage['href'].encode('utf-8')
        href = href.split(",")
        listings_per_page = re.sub('\W+', '', href[1])  # removes special characters
        total_search_pages = href[0][
                             -3:]  # Extracts the last 3 characters of the string which is the total pages in the search results
        return listings_per_page, total_search_pages


def main():
    raw_html = "http://www.boattrader.com/search-results/NewOrUsed-any/Type-any/Category-all/Zip-33647/Radius-200/Sort-Updated:DESC/Page-1,28?"  # you'll need to define this.
    page_number = 1
    count_per_page, total_pages = find_search_results_details(raw_html)
    # count_per_page=28
    # total_pages=2
    flag = 0  # to maintain record of headers
    while page_number <= total_pages:
        linklist = []
        details = {}
        # raw_html = "http://www.boattrader.com/search-results/NewOrUsed-any/Type-any/Category-all/Zip-33647/Radius-200/Sort-Updated:DESC/Page-61,28?"  # you'll need to define this.
        raw_html = "http://www.boattrader.com/search-results/NewOrUsed-any/Type-any/Category-all/Zip-33647/Radius-200/Sort-Updated:DESC/Page-%s,%s"%(page_number,count_per_page)# you'll need to define this.
        r = requests.get(raw_html)
        raw_html = r.text
        # we start with getting the soup for each page.
        bs_struct = BeautifulSoup(raw_html, "html.parser")
        # we then look for all the <li>
        for listing in bs_struct.find_all('section', {'class': 'boat-listings'}):  # refer to the HTML sample below
            for ol_tag in listing.find_all('ol', {'class': 'boat-list'}):
                for listing_link in ol_tag.find_all('li'):
                    links = listing_link.find_all('a', href=True)
                    if len(links) != 0:  # make sure it found something.
                        link = links[0]
                        # university_name = link.text.encode('utf-8') # some encodi   ng issue, you can ignore this.
                        url = link['href'].encode('utf-8')
                        # scrape_university_links(url)# You can further scrape the university link here.
                        linklist.append(url)  # increment the page starting index
        page_number += 1
        # Enter Each listing and find information

        for each_listing in linklist:
            each_listing = "http:" + each_listing
            ad_page = Open_listing(each_listing)
            details[each_listing] = [fetch_AdInfo(ad_page)]

        flag = write_to_excel(details, flag)
        print "Completed Processing Page: %s out of %s " % (page_number - 1, total_pages)


main()