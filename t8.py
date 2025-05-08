from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# Set up the WebDriver
driver = webdriver.Chrome()
driver.maximize_window()
driver.get('https://www.propertyfinder.ae/en/find-agent/search?page=1')

# List to hold all the broker data
brokers_data = []
page_number = 1

while True:
    print(f"Scraping page {page_number}...")

    # Wait for the list to load properly
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "(//ul[@aria-label='Matching agents'])[1]/li"))
    )

    # Count the number of boxes
    agent_count = len(driver.find_elements(By.XPATH, "(//ul[@aria-label='Matching agents'])[1]/li"))
    print(f"Found {agent_count} agents on page {page_number}.")

    # Loop through each agent box using XPath index
    for index in range(1, agent_count + 1):
        print(f"Processing profile {index} on page {page_number}")

        # XPath for the specific box
        xpath = f"(//ul[@aria-label='Matching agents'])[1]/li[{index}]"
        
        try:
            # Find the element and scroll into view
            person = driver.find_element(By.XPATH, xpath)
            driver.execute_script("arguments[0].scrollIntoView();", person)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", person)
        except Exception as e:
            print(f"Skipping profile {index} due to click failure: {e}")
            continue

        # Wait for the profile page to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'styles_agent-hero-section__info-item--bold__nEM5q'))
            )
        except Exception as e:
            print(f"Failed to load profile {index}, skipping...")
            driver.back()
            time.sleep(2)
            continue

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
            print(f"Error locating table for profile {index}: {e}")
            driver.back()
            time.sleep(2)
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
            EC.presence_of_all_elements_located((By.XPATH, "(//ul[@aria-label='Matching agents'])[1]/li"))
        )

    # Find the next page button
    try:
        next_button = driver.find_element(By.XPATH, "//a[@aria-label='Next']")
        if "disabled" in next_button.get_attribute("class"):
            print("No more pages found. Scraping complete.")
            break
        driver.execute_script("arguments[0].click();", next_button)
        page_number += 1
        time.sleep(3)
    except Exception as e:
        print(f"No more pages to scrape: {e}")
        break

# Close the driver
driver.quit()

# Save the data to JSON
output_file = 'brokers_data.json'
with open(output_file, 'w') as json_file:
    json.dump(brokers_data, json_file, indent=2)

print(f"Data saved to {output_file}")
