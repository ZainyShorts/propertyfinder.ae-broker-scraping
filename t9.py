from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# Set up the WebDriver
driver = webdriver.Chrome()
driver.get('https://www.propertyfinder.ae/en/find-agent/search?page=1')

# Wait for the elements to load properly
WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.XPATH, "(//ul[@aria-label='Matching agents'])[1]/li"))
)

# List to hold all the broker data
brokers_data = []

# Loop through the elements and click them one by one
index = 0
while True:
    try:
        # Re-fetch the list of people elements using the new XPath
        people = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, "(//ul[@aria-label='Matching agents'])[1]/li"))
        )

        if index >= len(people):
            print("No more profiles to click.")
            break

        # Scroll and click the element
        driver.execute_script("arguments[0].scrollIntoView();", people[index])
        people[index].click()
        print(f"Clicked on profile {index + 1}")

        # Wait for the profile page to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'styles_agent-hero-section__info-item--bold__nEM5q'))
        )

        # Scrape the name
        name = driver.find_element(By.CLASS_NAME, 'styles_agent-hero-section__info-item--bold__nEM5q').text

        # Scrape the company name
        try:
            company = driver.find_element(By.CLASS_NAME, 'styles_broker__name__uSCaR').text
        except:
            company = "Not specified"

        # Initialize a set to store unique property types
        unique_property_types = set()

        # Locate the table and extract property types
        try:
            table = driver.find_element(By.XPATH, "//table[@class='table-module_table__L2zfY']")
            rows = table.find_elements(By.XPATH, ".//tbody/tr")

            # Loop through each row to extract the 4th column (Property Type)
            for row in rows:
                try:
                    property_type = row.find_element(By.XPATH, ".//td[4]").text.strip()
                    if property_type:
                        unique_property_types.add(property_type)
                except Exception as e:
                    print(f"Error extracting property type for row: {e}")
                    continue

        except Exception as e:
            print(f"Error locating table: {e}")

        # Add data to the list as an object
        brokers_data.append({
            "name": name,
            "company": company,
            "propertyType": list(unique_property_types)  # Converting set to list for JSON serialization
        })

        # Navigate back to the main page
        driver.back()

        # Wait for the list to reload
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "(//ul[@aria-label='Matching agents'])[1]/li"))
        )

        # Increment the index
        index += 1

    except Exception as e:
        print(f"An error occurred: {e}")
        continue
        # break


# Close the driver
driver.quit()

# Save the data to JSON
output_file = 'brokers_data.json'
with open(output_file, 'w') as json_file:
    json.dump(brokers_data, json_file, indent=2)

print(f"Data saved to {output_file}")
