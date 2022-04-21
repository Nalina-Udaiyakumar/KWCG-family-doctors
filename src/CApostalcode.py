#Python 3
## Code to scrape all postal codes in KWCG area to search doctors based on location

# libraries
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

import time
import os
import pandas as pd
import numpy as np
import pgeocode

# Set working directory
os.chdir(r"---Directory path---")
print(os.getcwd())

## Open a chrome session using Selenium chrome web driver
DRIVER_PATH = '---Path to Chromedriver---'
driver = webdriver.Chrome()

## Scrape postal codes in Waterloo
# Open the URL
link = "https://postal-codes.cybo.com/canada/waterloo-ontario/"
driver.get(link)
pcWaterloo = driver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div[8]/div[2]')
pcWaterloo = pcWaterloo.text
print(len(pcWaterloo))
waterlooCodes = pcWaterloo.splitlines()
print(len(waterlooCodes))  # should be 2772
waterlooCodes = [str(x) for x in waterlooCodes]  # Convert unicode list to list of strings
print(waterlooCodes)
waterlooCodes = list(zip(waterlooCodes,np.repeat('Waterloo',len(waterlooCodes))))

## Scrape postal codes in Cambridge
# Open URL
link = "https://postal-codes.cybo.com/canada/cambridge-ontario/"
driver.get(link)
pcCambridge = driver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div[8]/div[2]')
pcCambridge = pcCambridge.text
print(len(pcCambridge))
cambridgeCodes = pcCambridge.splitlines()
print(len(cambridgeCodes))   # should be 3830
cambridgeCodes = [str(x) for x in cambridgeCodes]  # Convert unicode list to list of strings
print(cambridgeCodes)
cambridgeCodes = list(zip(cambridgeCodes,np.repeat('Cambridge',len(cambridgeCodes))))

## Scrape postal codes in Guelph
# Open URL
link = "https://postal-codes.cybo.com/canada/guelph/"
driver.get(link)
pcGuelph = driver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div[8]/div[2]')
pcGuelph = pcGuelph.text
print(len(pcGuelph))
guelphCodes = pcGuelph.splitlines()
print(len(guelphCodes))   # should be 3676
guelphCodes = [str(x) for x in guelphCodes]  # Convert unicode list to list of strings
print(guelphCodes)   
guelphCodes = list(zip(guelphCodes,np.repeat('Guelph',len(guelphCodes))))

KWCGpostcodes = pd.DataFrame(waterlooCodes, columns = ['Postalcode', 'City'])
KWCGpostcodes = KWCGpostcodes.append(pd.DataFrame(cambridgeCodes, columns = ['Postalcode', 'City']))
KWCGpostcodes = KWCGpostcodes.append(pd.DataFrame(guelphCodes, columns = ['Postalcode', 'City']))
print(KWCGpostcodes.head(10))
print(KWCGpostcodes.shape)

## Scrape postal codes in Kitchener
linkslist = ['https://postal-codes.cybo.com/canada/N2A_kitchener-ontario/', #633
             'https://postal-codes.cybo.com/canada/N2B_kitchener-ontario/', #519
             'https://postal-codes.cybo.com/canada/N2C_kitchener-ontario/', #322
             'https://postal-codes.cybo.com/canada/N2E_kitchener-ontario/', #644
             'https://postal-codes.cybo.com/canada/N2G_kitchener-ontario/', #558
             'https://postal-codes.cybo.com/canada/N2H_kitchener-ontario/', #892
             'https://postal-codes.cybo.com/canada/N2K/',                   #627
             'https://postal-codes.cybo.com/canada/N2M_kitchener-ontario/', #824
             'https://postal-codes.cybo.com/canada/N2N_kitchener-ontario/', #467
             'https://postal-codes.cybo.com/canada/N2P_kitchener-ontario/', #359
             'https://postal-codes.cybo.com/canada/N2R_kitchener-ontario/'] #197

for link in linkslist: 
    # Open URL
    print(link)
    driver.get(link)
    
    #wait for page to load
    time.sleep(3)
    
    try:
        moreButton = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/div[2]/table/tbody/tr[12]/td[2]/a[11]')
        moreButton.click()
    except NoSuchElementException:  # The more button may be in a different position in some pages or the page may not load in certain cases
        driver.get(link)
        time.sleep(3)
        try: 
            moreButton = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/div[2]/table/tbody/tr[11]/td[2]/a[11]')
            moreButton.click()
        except NoSuchElementException: # Pass if the more button cannot be located in the alternate location - iterate next link
            pass
        

    pcKitchener = driver.find_element_by_xpath('/html/body/div[5]/div[2]/div/table/tbody')
    pcKitchener = pcKitchener.text

    kitchenerCodes = pcKitchener.splitlines()
    kitchenerCodes = [str(x) for x in kitchenerCodes]
    print(len(kitchenerCodes))
    kitchenerCodes = list(zip(kitchenerCodes,np.repeat('Kitchener',len(kitchenerCodes))))

    KWCGpostcodes = KWCGpostcodes.append(pd.DataFrame(kitchenerCodes, columns = ['Postalcode', 'City']))
    # end of for loop

# remove duplicate postal codes if any
KWCGpostcodes.drop_duplicates(subset='Postalcode',keep='first',inplace=True)
print(KWCGpostcodes.shape)

### -------- Find latitude and logitude coordinates for each postal code - using pgeocode
KWCGpostcodes['Latitude'] = 0.00
KWCGpostcodes['Longitude'] = 0.00

for i,eachcode in KWCGpostcodes['Postalcode'].items():
    latlong = nomi.query_postal_code(eachcode)
    KWCGpostcodes.at[i,'Latitude'] = latlong.latitude
    KWCGpostcodes.at[i,'Longitude'] = latlong.longitude
    # end of for loop

print(KWCGpostcodes.shape)
print(KWCGpostcodes.head(10))

# KWCGpostcodes.to_csv("KWCGpostcodes_Latlong.csv",header=True, index=False) #save to csv file
uniqueKWCGcodes = KWCGpostcodes
uniqueKWCGcodes.drop_duplicates(subset=['Latitude','Longitude'],keep = 'first', inplace=True)
print(uniqueKWCGcodes)  #There are only 29 unique Lat-long postal codes in KWCG area. We can build an effective distance matrix based only on these 29 postalcodes
