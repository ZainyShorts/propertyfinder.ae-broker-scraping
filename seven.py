from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import pandas as pd
import os

# Set up the WebDriver
driver = webdriver.Chrome()
page_number = 301
total_pages = 350

# Initialize lists to hold data and broken links
broken_links = []
brokers_data = []

# File paths
json_file_path = 'five.json'
excel_file_path = 'five.xlsx'

# If JSON file exists, load existing data
if os.path.exists(json_file_path):
    with open(json_file_path, 'r') as file:
        brokers_data = json.load(file)

# Start page scraping
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

                try:
                    show_all_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='show-all']"))
                    )
                    driver.execute_script("arguments[0].click();", show_all_button)
                    print("Clicked 'Show All' button")

                    # Wait for the table to expand and load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//table[@class='table-module_table__L2zfY']"))
                    )
                    print("Table data loaded successfully.")
                except Exception as e:
                    print(f"'Show All' button not found or could not be clicked: {e}")

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
                    print(f"Table not found or could not be loaded, skipping this profile. Error: {e}")
                    # Skip to the next person if the table is not found
                    index += 1
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
            "profile": "Failed to load page",
            "page": page_number
        })
        page_number += 1
        continue

    # Increment to the next page
    page_number += 1

    # Every 20 entries, append to JSON file
    if len(brokers_data) % 20 == 0:
        print("Saving to JSON file...")

        # Save the data to JSON
        with open(json_file_path, 'w') as json_file:
            json.dump(brokers_data, json_file, indent=2)

        # Also update the Excel file
        df = pd.DataFrame(brokers_data)
        df.to_excel(excel_file_path, index=False)

# Close the driver
driver.quit()
