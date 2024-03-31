from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import csv

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'  
driver = webdriver.Chrome(options=chrome_options)

url = 'https://www.airtel.com.ng/voice/international_calls/international_calling_rate'  # Replace this with the URL of the website


driver.get(url)

# Find the dropdown menu element, find options and extract their element
select_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'selectCountry')))
options = select_element.find_elements(By.TAG_NAME, 'option')

# Write to CSV
with open('Airtel_countries_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Country', 'Zone Countries', 'Zones', 'Tariff', 'Country Codes', 'Exception? (Y/N)', 'Billing']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    # Loop through each option in the dropdown
    for option in options:
        value = option.get_attribute('value')
        country_name = option.text.strip()
        if value and country_name:  # Skip the first option which is "Select a country"
            # Select the country from the dropdown
            option.click()
            
            try:
                # Wait until the table with class 'table-responsive' is present
                table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.table-responsive table.table')))
                
                # Extract data from the table
                rows = table.find_elements(By.TAG_NAME, 'tr')
                for row in rows:
                    columns = row.find_elements(By.TAG_NAME, 'td')
                    if len(columns) == 6:  # Ensure it's a valid row with 4 columns
                        country_data = {
                            'Country': country_name,
                            'Zone Countries': columns[0].text.strip(),
                            'Zones': columns[1].text.strip(),
                            'Tariff': columns[2].text.strip(),
                            'Country Codes': columns[3].text.strip(),
                            'Exception? (Y/N)': columns[4].text.strip(),
                            'Billing': columns[5].text.strip()
                        }
                        writer.writerow(country_data)
                
                writer.writerow({})  
            except TimeoutException:
                print(f"Timeout occurred: Table not found for country '{country_name}'")
                
driver.quit()
