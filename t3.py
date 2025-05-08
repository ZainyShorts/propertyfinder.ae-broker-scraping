from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up the WebDriver
driver = webdriver.Chrome()
driver.get('https://www.propertyfinder.ae/en/find-agent/search?page=1')

# Wait for the elements to load properly
WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, 'styles_item__YzikE'))
)

# Initialize a set to store unique property types
unique_property_types = set()

# Loop through each profile
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
        people[index].click()
        print(f"Clicked on profile {index + 1}")

        # Wait for the profile page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'styles_agent-hero-section__info-item--bold__nEM5q'))
        )

        # Locate the table
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

# Display the unique property types
print("Unique Property Types Found:")
for p_type in unique_property_types:
    print(f"- {p_type}")
