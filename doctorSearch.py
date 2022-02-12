from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

import time
import os
import pandas as pd
import numpy as np

# Set working directory
os.chdir("---Your directory path---")
print(os.getcwd())

# Define function scrape_doctors to scrape the results
def scrape_doctors():
    # Number of pages of results available
    noOfPages = driver.find_element_by_xpath('/html/body/form/section/div/div/div[3]/div[1]/div[1]/div[2]/p')
    noOfPages = noOfPages.text
    print(noOfPages)
    noOfPages = noOfPages.split(' ')
    noOfPages = int(noOfPages[3])
    print("Number of pages: {}".format(noOfPages))
    
    # Create a df to hold all results for the selected city
    resultsDf = pd.DataFrame(columns=['Name', 'ID', 'Location', 'Details'])
    print(resultsDf)

    for i in range(1,noOfPages+1):
        # Getting the current page from the webpage
        currentPage = driver.find_element_by_xpath('/html/body/form/section/div/div/div[3]/div[1]/div[1]/div[2]/p')
        currentPage = currentPage.text
        currentPage = currentPage.split(" ")
        currentPage = int(currentPage[1])

        # Getting a list of all the results in the current page
        listOfArticles = driver.find_elements_by_tag_name('article')

        print("Iteration number: {}".format(i))
        print("Number of results in page %s is: %s" %(currentPage, len(listOfArticles)))

        for article in listOfArticles:
            name = article.find_element_by_xpath('.//h3/a').text
            idno = article.find_element_by_xpath('.//h3').text
            location = article.find_element_by_xpath('.//p').text
            try:
                details = article.find_element_by_xpath('.//div/p').text
            except NoSuchElementException:  # The specialisations and other notes are unavailable for certain results
                details = np.nan
                pass

            resultsDf = resultsDf.append([{'Name':name, 'ID':idno, 'Location':location, 'Details':details}],
                                               ignore_index=True) 
            # ignore_index sets the index to continuos number instead of 0 for each row

        # Print the shape of dataframe in each iteration 
        print("The size of dataframe at the end of iteration {} is {}".format(i,resultsDf.shape))

        if(i==noOfPages):
            break

        if(i%5==1):
            nextPageButton = driver.find_element_by_id('p_lt_ctl01_pageplaceholder_p_lt_ctl03_CPSO_DoctorSearchResults_rptPages_ctl01_lnbPage')

        if(i%5==2):
            nextPageButton = driver.find_element_by_id('p_lt_ctl01_pageplaceholder_p_lt_ctl03_CPSO_DoctorSearchResults_rptPages_ctl02_lnbPage')

        if(i%5==3):
            nextPageButton = driver.find_element_by_id('p_lt_ctl01_pageplaceholder_p_lt_ctl03_CPSO_DoctorSearchResults_rptPages_ctl03_lnbPage')

        if(i%5==4):
            nextPageButton = driver.find_element_by_id('p_lt_ctl01_pageplaceholder_p_lt_ctl03_CPSO_DoctorSearchResults_rptPages_ctl04_lnbPage')

        if(i%5==0):
            nextPageButton = driver.find_element_by_id('p_lt_ctl01_pageplaceholder_p_lt_ctl03_CPSO_DoctorSearchResults_lnbNextGroup')

        nextPageButton.click()
        # Introducing a wait time for the page to load
        time.sleep(2)

        # End of for loop to iterate over each page
    print('The total number of results scraped: {}'.format(resultsDf.shape))  
    
    return resultsDf
# End of function


## Open a chrome session using Selenium chrome web driver
DRIVER_PATH = '---Path to chromedriver---'
driver = webdriver.Chrome()

## --------------------------------------------------------------------
##Scrape family physicians in Kitchener
# Opening the URL for CPSO doctor search
link = "https://doctors.cpso.on.ca/?search=general"
driver.get(link)
# Select the dropdown button for choosing the city
cityDropdown = Select(driver.find_element_by_id('p_lt_ctl01_pageplaceholder_p_lt_ctl02_CPSO_AllDoctorsSearch_ddCity'))
# 1. Select the city of Kitchener from the dropdown
cityDropdown.select_by_value('1515') #Pass value as string
# Select family physicians only
familyDoc = driver.find_element_by_xpath('/html/body/form/section/div/div/div[2]/div/div/div/div[1]/div/div[3]/div[3]/div[2]/div/section[1]/fieldset/div[1]/label[1]')
familyDoc.click()
# Click the submit button
submitButton = driver.find_element_by_id('p_lt_ctl01_pageplaceholder_p_lt_ctl02_CPSO_AllDoctorsSearch_btnSubmit1')
submitButton.click()
# Introducing a wait time for the page to load
time.sleep(5)
kitchenerDoctors = scrape_doctors()


## --------------------------------------------------------------------
## Scrape family physicians in Waterloo
# Opening the URL for CPSO doctor search
link = "https://doctors.cpso.on.ca/?search=general"
driver.get(link)
# Select the dropdown button for choosing the city
cityDropdown = Select(driver.find_element_by_id('p_lt_ctl01_pageplaceholder_p_lt_ctl02_CPSO_AllDoctorsSearch_ddCity'))
# 2. Select the city of Waterloo from the dropdown
cityDropdown.select_by_value('2017') #Pass value as string
# Select family physicians only
familyDoc = driver.find_element_by_xpath('/html/body/form/section/div/div/div[2]/div/div/div/div[1]/div/div[3]/div[3]/div[2]/div/section[1]/fieldset/div[1]/label[1]')
familyDoc.click()
# Click the submit button
submitButton = driver.find_element_by_id('p_lt_ctl01_pageplaceholder_p_lt_ctl02_CPSO_AllDoctorsSearch_btnSubmit1')
submitButton.click()
# Introducing a wait time for the page to load
time.sleep(5)
waterlooDoctors = scrape_doctors()


## --------------------------------------------------------------------
## Scrape family physicians in Cambridge
# Opening the URL for CPSO doctor search
link = "https://doctors.cpso.on.ca/?search=general"
driver.get(link)
# Select the dropdown button for choosing the city
cityDropdown = Select(driver.find_element_by_id('p_lt_ctl01_pageplaceholder_p_lt_ctl02_CPSO_AllDoctorsSearch_ddCity'))
# 3. Select Cambridge from the dropdown
cityDropdown.select_by_value('1164') #Pass value as string
# Select family physicians only
familyDoc = driver.find_element_by_xpath('/html/body/form/section/div/div/div[2]/div/div/div/div[1]/div/div[3]/div[3]/div[2]/div/section[1]/fieldset/div[1]/label[1]')
familyDoc.click()
# Click the submit button
submitButton = driver.find_element_by_id('p_lt_ctl01_pageplaceholder_p_lt_ctl02_CPSO_AllDoctorsSearch_btnSubmit1')
submitButton.click()
# Introducing a wait time for the page to load
time.sleep(5)
cambridgeDoctors = scrape_doctors()


## --------------------------------------------------------------------
## Scrape family physicians in Guelph
# Opening the URL for CPSO doctor search
link = "https://doctors.cpso.on.ca/?search=general"
driver.get(link)
# Select the dropdown button for choosing the city
cityDropdown = Select(driver.find_element_by_id('p_lt_ctl01_pageplaceholder_p_lt_ctl02_CPSO_AllDoctorsSearch_ddCity'))
# 4. Select Guelph from the dropdown
cityDropdown.select_by_value('1417') #Pass value as string
# Select family physicians only
familyDoc = driver.find_element_by_xpath('/html/body/form/section/div/div/div[2]/div/div/div/div[1]/div/div[3]/div[3]/div[2]/div/section[1]/fieldset/div[1]/label[1]')
familyDoc.click()
# Click the submit button
submitButton = driver.find_element_by_id('p_lt_ctl01_pageplaceholder_p_lt_ctl02_CPSO_AllDoctorsSearch_btnSubmit1')
submitButton.click()
# Introducing a wait time for the page to load
time.sleep(5)
guelphDoctors = scrape_doctors()


## --------------------------------------------------------------------
## Consolidating scraped results
kitchenerDoctors['City'] = 'Kitchener'
waterlooDoctors['City'] = 'Waterloo'
cambridgeDoctors['City'] = 'Cambridge'
guelphDoctors['City'] = 'Guelph'
## Combining all the results dataframes to clean and structure the data
allDocsDf = kitchenerDoctors
allDocsDf = allDocsDf.append([waterlooDoctors,cambridgeDoctors,guelphDoctors],
                             ignore_index = True)
print(allDocsDf.shape)
print(allDocsDf.head(10))

allDocsDf[['LastName','FirstName']] = allDocsDf['Name'].str.split(',', expand = True)
allDocsDf['CPSOID'] = allDocsDf['ID'].str.extract('([0-9]+)',expand=False)
allDocsDf['Location'] = allDocsDf['Location'].replace({"\\n":" "}, regex=True)
# extract phone and fax numbers
allDocsDf[['Location','Phone']] = allDocsDf['Location'].str.split("Phone:",expand=True)
allDocsDf[['Phone','Fax']] = allDocsDf['Phone'].str.split("Fax:",expand=True)
# extract postal codes from the address
allDocsDf['Postal Code'] = allDocsDf['Location'].str.extract('([A-Z]\d[A-Z]\s?\d[A-Z]\d)', expand=False)
# Extract the additional practice locations to a new column
allDocsDf[['Details','Additional Locations']] = allDocsDf['Details'].str.split("This doctor has additional practice locations in:", expand=True)
allDocsDf[['Details','Former Name']] = allDocsDf['Details'].str.split("Former Name:", expand=True)
# Rename and delete columns
allDocsDf = allDocsDf.rename(columns={"Details":"Specializations"})
allDocsDf = allDocsDf.drop("ID", axis=1)

print(allDocsDf.shape)

# Merge the doctors per location count column
locationTable = pd.DataFrame(allDocsDf['Location'].value_counts().reset_index())
locationTable.columns = ['Location','LocationCount']
allDocsDf = pd.merge(allDocsDf,locationTable, on='Location')
allDocsDf['LocationFlag'] = np.where(allDocsDf['LocationCount']>1,"Multiple doctors", "Single practitioner location")
allDocsDf = allDocsDf.drop("LocationCount", axis=1)
print(allDocsDf.shape)
print(allDocsDf.head(20))

# Getting phone numbers of practice locations with more doctors associated with it, in descending order
print("Phone numbers associated with multiple doctors: ")
print(allDocsDf['Phone'].value_counts())
phoneTable = pd.DataFrame(allDocsDf['Phone'].value_counts().reset_index())
phoneTable.columns = ['Phone','PhoneCount']
phoneTable = pd.merge(phoneTable,allDocsDf[['Phone','Location','City']], on='Phone', how="left")
phoneTable = phoneTable.drop_duplicates(subset=None, keep='first', inplace=False)
print(phoneTable.shape)
print(phoneTable.head(10))
phoneTable.to_csv('Phone directory.csv', header=True)


# Write the results in a csv file
allDocsDf.to_csv('Results_family doctors KWCG.csv', header=True)
