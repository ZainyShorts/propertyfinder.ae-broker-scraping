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
page_number = 1
total_pages = 500

# Initialize lists to hold data and broken links
broken_links = []
brokers_data = []

# File paths
json_file_path = 'brokers_data.json'
excel_file_path = 'brokers_data.xlsx'

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

                # NEW: Click the "Show All" button if it exists
                try:
                    show_all_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Show All']"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView(true);", show_all_button)
                    time.sleep(1)  # Give some time for smooth scroll
                    show_all_button.click()
                    print("Clicked 'Show All' button")
                except Exception as e:
                    print(f"'Show All' button not found or could not be clicked: {e}")

                time.sleep(1)
                
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
            "profile": "Failed to load page",
            "page": page_number
        })
        page_number += 1
        continue

    # Increment to the next page
    page_number += 1

    if page_number == 3:  # Limit for testing
        break

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
