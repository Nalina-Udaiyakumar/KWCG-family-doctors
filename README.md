# KWCG-family-doctors
Scrape list of all family medicine practitioners in the Kitchener area - Kitchener, Waterloo, Cambridge &amp; Guelph 

Develop an interactive dashboard on Python dash app for users to search family doctors based on city, postal code and radius of proximity using interactive input controls. Enable download of the filtered search results as an Excel file.

Using Selenium webdriver(chrome) to scrape the list of currently practicing family doctors in Kitchener Waterloo area along with their details like full name, ID, phone, specializations and location of practice to create a family doctor database. Curate database of postal codes in Kitchener Waterloo region, their latitude and longitude to create distance matrix between any two postal codes. 


Scraping information from: College of Physicians and Surgeons of Ontario (CPSO) website
About CPSO:https://www.cpso.on.ca/About/What-we-do

Doctor search URL from CPSO website: https://doctors.cpso.on.ca/?search=general 

![KW doctor search dashboard](https://user-images.githubusercontent.com/15101045/182699992-c25a8bdf-a99e-4ace-b169-98154f519f22.png)



Possible improvements:
1. Improve the code to include scraping gender information of the doctor
2. Modify the code to select specialists of interest and scrape the results
3. Create a map of the scraped results

