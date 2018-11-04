# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 22:23:45 2018

@author: gezis
"""

import requests
import json
import re
from bs4 import BeautifulSoup
from collections import OrderedDict


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

r=requests.get('https://www.redfin.com/zipcode/21043', headers=headers)
r.status_code

#r.text

reg_property_history_row = re.compile('propertyHistory\-[0-9]+')
reg_property_urls = re.compile('(/[A-Z][A-Z]/[A-Za-z\-/0-9]+/home/[0-9]+)')


property_urls = reg_property_urls.findall(r.text.replace('\\u002F', '/'))
property_urls = list(set(property_urls))


output_data = []

for property_url in property_urls:
    page_source=requests.get('https://www.redfin.com'+property_url, headers=headers).text
    #page_source
    
    soup = BeautifulSoup(page_source, 'html.parser')
    property_data = OrderedDict()
    
    #  use try catch to handle when a data point is not available
    try:
        property_data['street_address'] = soup.find('span', attrs={'itemprop': 'streetAddress'}).get_text()
    except:
        property_data['street_address'] = 'N/A';print('street_address not found')
    try:
        property_data['address_locality'] = soup.find('span', attrs={'itemprop': 'addressLocality'}).get_text()
    except:
        property_data['address_locality'] = 'N/A';print('address_locality not found')
    try:
        property_data['address_region'] = soup.find('span', attrs={'itemprop': 'addressRegion'}).get_text()
    except:
        property_data['address_region'] = 'N/A';print('address_region not found')
    try:
        property_data['postal_code'] = soup.find('span', attrs={'itemprop': 'postalCode'}).get_text()
    except:
        property_data['postal_code'] = 'N/A';print('postal_code not found')
    try:
        property_data['price'] = soup.find('div', attrs={'class': 'info-block price'}).find('div').get_text()
    except:
        property_data['price'] = 'N/A';print('price not found')
    try:
        property_data['beds'] = soup.find('div', attrs={'data-rf-test-id': 'abp-beds'}).find('div').get_text()
    except:
        property_data['beds'] = 'N/A';print('beds not found')
    try:
        property_data['baths'] = soup.find('div', attrs={'data-rf-test-id': 'abp-baths'}).find(
            'div').get_text()
    except:
        property_data['baths'] = 'N/A';print('baths not found')
    try:
        property_data['sqFt'] = soup.find('div', attrs={'data-rf-test-id': 'abp-sqFt'}).find('span', attrs={
            'class': 'statsValue'}).get_text()
    except:
        property_data['sqFt'] = 'N/A';print('sqFt not found')
    try:
        property_data['price_per_sqFt'] = soup.find('div', attrs={'data-rf-test-id': 'abp-sqFt'}).find('div',
                                                                                                            attrs={
                                                                                                                "data-rf-test-id": "abp-priceperft"}).get_text()
    except:
        property_data['price_per_sqFt'] = 'N/A';print('price_per_sqFt not found')

    
    try:
        property_data['status'] = soup.find('span', attrs={"data-rf-test-id": "abp-status"}).find('span',
                                                                                                       attrs={
                                                                                                           'class': 'value'}).get_text()
    except:
        property_data['status'] = 'N/A';print('status not found')
        
    # longitude and latitude
    try:
        property_data['latitude'] = soup.find('meta', attrs={'itemprop': 'latitude'}).get("content")
    except:
        property_data['latitude'] = 'N/A';print('latitude not found')
    try:
        property_data['longitude'] = soup.find('meta', attrs={'itemprop': 'longitude'}).get("content")
    except:
        property_data['longitude'] = 'N/A';print('longitude not found')
    
        
    property_data['propert_history'] = []
    for row in soup.find_all('tr', attrs={'id': reg_property_history_row}):
        data_cells = row.find_all('td')
        history_data_row = OrderedDict()
        history_data_row['date'] = data_cells[0].get_text()
        history_data_row['event & source'] = data_cells[1].get_text()
        history_data_row['price'] = data_cells[2].get_text()
        history_data_row['appreciation'] = data_cells[3].get_text()
        property_data['propert_history'].append(history_data_row)
        
        
    property_data['school'] = []
    for row in soup.find('table', attrs={'class': 'basic-table-3'}).find_all('tr')[1:]:
        data_cells = row.find_all('td')
        school_data_row = OrderedDict()
        school_data_row['name'] = re.search('(.*?School)', data_cells[0].get_text()).group(0)
        school_data_row['rating'] = data_cells[1].get_text()
        school_data_row['distance'] = data_cells[3].get_text()
        property_data['school'].append(school_data_row)
    
    property_data['url'] = 'https://www.redfin.com' + property_url
    
    output_data.append(property_data)


property_data


# write to a json file
open('redfin_output.json', 'w').write(json.dumps(output_data, indent=4))