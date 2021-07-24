
# In[6]:


import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import os
import math
from datetime import date

os.makedirs('Assisted Living', exist_ok=True)
os.makedirs('Independent Living', exist_ok=True)


# In[7]:


url = "https://www.brookdale.com/en.html"
  
driver = webdriver.Chrome('C:/drivers/chromedriver') 
driver.get(url) 
driver.maximize_window()
time.sleep(2) 
  
html = driver.page_source


# In[8]:


element = driver.find_element_by_xpath('//div[@class="ctcore-header__community-search"]')
element.click()

element = driver.find_element_by_xpath('//a[@href="/en/locations.html"]')
element.click()
time.sleep(2) 


html = driver.page_source

soup = BeautifulSoup(html, "html.parser")
states_tags = soup.find_all('a', {'class' : "state-list__state-link"})

states=[]
Total_Property = []
Date = []

for state in states_tags:
    states.append(state.text)

for state in states:
    print("Going into the "+ state + ' state')
    element= driver.find_element_by_link_text(state)
    element.click()
    time.sleep(5) 

    element = driver.find_element_by_xpath('//select[@id="globalsearch-caretype"]')
    element.click()

    types_=["Assisted Living", "Independent Living"]
    
    unique_places=[]
    
    for type_ in types_:
        print("Scraping the "+ type_ + ' data')

        element = driver.find_element_by_xpath('//option[@data-name='+'"'+type_+'"'+']')
        element.click()
        time.sleep(5)


        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        tags = soup.find_all('a', {'class' : "globalsearch-results-item__title font-s-18 font-w-600 cap-links__link"})
        if tags:

            links=[]
            Names=[]
            for tag in tags:
                links.append(tag['href'][:-5]+"/details.html#communityLink")
                Names.append(tag.text)
                unique_places.append(str(tag.text))

            #properties = int(soup.find('div', {'class' : "globalsearch-heading globalsearch-search-status--top padding-b-20 line-h-1-3"}).find("span" , recursive=False).text)
            #pages=math.floor(properties/5)
            pages = 0 
            last = soup.find('li', {'class' : "paginationjs-page paginationjs-last J-paginationjs-page"})
            next_ = soup.find_all('li', {'class' : "paginationjs-page J-paginationjs-page"})
            if last:
                pages = int(last.text) - 1
            elif next_:
                pages = len(next_)
                    
            for page in range(pages):
                driver.execute_script('$(".paginationjs-next.J-paginationjs-next").click()')
                time.sleep(2)
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")

                tags = soup.find_all('a', {'class' : "globalsearch-results-item__title font-s-18 font-w-600 cap-links__link"})
                for tag in tags:
                    links.append(tag['href'][:-5]+"/details.html#communityLink")
                    Names.append(tag.text)
                    unique_places.append(str(tag.text))



            Amenities=[]
            Address=[]
            Types=[]
            for link in links:
                response = requests.get(link)
                page_contents = response.text
                t_doc = BeautifulSoup(page_contents, 'html.parser')
                tags = t_doc.find_all('ul', {'name' : "amenitiesList"})
                lis = ""
                for ul in tags:
                    for li in ul.findAll('li'):
                        if li.find('ul'):
                            break
                        lis+=str(li.text)
                        lis+=", "

                Amenities.append(lis)     
                tags = t_doc.find('div', {'class' : "address"}).find("div" , recursive=False).find("a" , recursive=False)
                Address.append(str(tags.text))

                tags = t_doc.find_all('ul', {'class' : "cd-header__loc-list ctcore-util-unlist"})
                lis = ""
                for ul in tags:
                    for li in ul.findAll('li'):
                        if li.find('ul'):
                            break
                        lis+=str(li.text)
                        lis+=", "
                Types.append(lis)

            final_dict={
            'Name' : Names,
            'Types' : Types,
            'Address' : Address,
            'Amenities' : Amenities
            }
            final_df = pd.DataFrame(final_dict)

            print("Writing the "+ state + '.csv file into the ' + type_ +" folder")

            final_df.to_csv(type_+'/'+ state + '.csv',index=None)
    
    
    
    
    Total_Property.append(len(set(unique_places)))
    Date.append(str(date.today().strftime("%d/%m/%Y")))
    
        
    driver.execute_script("window.history.go(-1)")


# In[56]:


another_dict = {
    'State':states,
    'Properties':Total_Property,
    'Date of scraping':Date
}

another_df = pd.DataFrame(another_dict)
another_df.to_csv('overall.csv',index=None)


# In[57]:


print(another_df.to_string(index=False))


# In[222]:


driver.close()

