from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import pandas as pd

# Set up the WebDriver
driver = webdriver.Chrome()
driver.get('https://www.propertyfinder.ae/en/find-agent/search?page=1')

# Wait for the elements to load properly
WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, 'styles_item__YzikE'))
)

# List to hold all the broker data
brokers_data = []

# Loop through the elements and click them one by one
index = 0
while True:
    try:
        # Re-fetch the list of people elements
        people = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'styles_item__YzikE'))
        )

        if index >= len(people):
            print("No more profiles to click.")
            break
        
        # Scroll and click the element
        ActionChains(driver).move_to_element(people[index]).click().perform()
        print(f"Clicked on profile {index + 1}")

        # Wait for the profile page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'styles_agent-hero-section__info-item--bold__nEM5q'))
        )

        # Scrape the name
        name = driver.find_element(By.CLASS_NAME, 'styles_agent-hero-section__info-item--bold__nEM5q').text

        # Scrape the nationality
        try:
            nationality = driver.find_element(By.CLASS_NAME, 'styles_agent-hero-section__info-item-label___B8y5').text
        except:
            nationality = "Not specified"

         # Scrape the propertyType
        try:
            propertyType = driver.find_element(By.CLASS_NAME, 'table-module_table__body__9nNRk').text
        except:
            propertyType = "Not specified"

        # Scrape the propertyForSale
        try:
            company = driver.find_element(By.CLASS_NAME, 'styles_broker__name__uSCaR').text
        except:
            company = "Not specified"
        
  


            

        # Add data to the list
        brokers_data.append({
            "name": name,
            "company": company,
            "propertyType":propertyType,
        })

        # Navigate back to the main page
        driver.back()

        # Wait for the list to reload
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'styles_item__YzikE'))
        )

        # Increment the index
        index += 1

    except Exception as e:
        print(f"An error occurred: {e}")
        break

# Close the driver
driver.quit()

# Store the data in JSON format
with open('brokers_data.json', 'w') as json_file:
    json.dump(brokers_data, json_file, indent=2)

# Convert the JSON data to a DataFrame
df = pd.DataFrame(brokers_data)

# Save the DataFrame to an Excel file
output_path = 'brokers_data.xlsx'
df.to_excel(output_path, index=False)

output_path
