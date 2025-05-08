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
page_number = 1
total_pages = 500

# Initialize lists to hold data and broken links
broken_links = []
brokers_data = []

while page_number <= total_pages:
    print(f"Scraping Page: {page_number} of {total_pages}")
    try:
        # Navigate to the page URL
        driver.get(f'https://www.propertyfinder.ae/en/find-agent/search?page={page_number}')

        # Wait for the elements to load properly
        people = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'styles_item__YzikE'))
        )

        index = 0
        while index < len(people):
            try:
                # Re-fetch the list of people elements
                people = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'styles_item__YzikE'))
                )

                # Scroll and click the element
                ActionChains(driver).move_to_element(people[index]).click().perform()
                print(f"Clicked on profile {index + 1} on page {page_number}")

                # Wait for the profile page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'styles_agent-hero-section__info-item--bold__nEM5q'))
                )

                # Scrape the name
                try:
                    name = driver.find_element(By.CLASS_NAME, 'styles_agent-hero-section__info-item--bold__nEM5q').text
                except:
                    name = "Not specified"

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
                    continue

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
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'styles_item__YzikE'))
                )

                # Increment the index
                index += 1

            except Exception as e:
                print(f"An error occurred: {e}")
                broken_links.append({
                    "profile": index,
                    "page": page_number
                })
                index += 1
                continue

    except Exception as e:
        print(f"Failed to load page {page_number}: {e}")
        broken_links.append({
                "profile": "Failed to load pag",
                "page": page_number
                })
        index += 1
        page_number += 1
        continue

    # Increment to the next page
    page_number += 1

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
