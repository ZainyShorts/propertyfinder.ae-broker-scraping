from selenium import webdriver
from selenium.webdriver.common.by import By

# Set up WebDriver (adjust path as needed)
driver = webdriver.Chrome()  # or Firefox(), Edge(), etc.

# Go to the website
driver.get("https://www.propertyfinder.ae/en/agent/jack-beal-237572")  # replace with the actual URL

# Locate the table (using tag, class, id, XPath, or CSS selector)
table = driver.find_element(By.XPATH, "//table")  # You can be more specific if needed

# Extract rows
rows = table.find_elements(By.TAG_NAME, "tr")

# Loop through rows and columns
table_data = []
for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")  # use "th" for header cells
    row_data = [cell.text for cell in cells]
    if row_data:  # skip empty rows
        table_data.append(row_data)

# Print or store the data
for row in table_data:
    print(row)

# Close the browser
driver.quit()
