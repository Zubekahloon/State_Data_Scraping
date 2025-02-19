from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException


chrome_driver_path = "chromedriver-win64/chromedriver.exe"
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)
driver.implicitly_wait(10)


query = "district-of-columbia"
driver.get(f"https://rehabs.org/centers/{query}/")
print(f">>>>>>> {driver.title}")
time.sleep(5)


csv_filename = 'rehab/zRehabs_All_State_Data.csv'
with open(csv_filename, 'a', newline='', encoding='utf-8') as file:
    csvData = csv.writer(file)
    csvData.writerow(['State_Name', 'Name', 'Address', 'Contact'])

    
    while True:
        try:
            button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "show-more-facilities")))
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            driver.execute_script("arguments[0].click();", button)
            time.sleep(3)
        except TimeoutException:
            print(f"No More Facility Available in {query}")
            break

   
    facilityLinks = driver.find_elements(By.CSS_SELECTOR, "#facility-cards-wrapper>tbody>tr>td>h3>a")
    facility_count = len(facilityLinks)
    print(f"Total facilities found in {query}: {facility_count}")

    
    for i in range(facility_count):
        try:
            facilityLinks = driver.find_elements(By.CSS_SELECTOR, "#facility-cards-wrapper>tbody>tr>td>h3>a")
            if i >= len(facilityLinks):
                break
            
            facilityLink = facilityLinks[i]
            driver.execute_script("arguments[0].scrollIntoView(true);", facilityLink)
            time.sleep(2)
            
            try:
                driver.execute_script("arguments[0].click();", facilityLink)
            except Exception as e:
                print(f"Skipping facility {i+1} due to click error: {e}")
                continue
            
            
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "outline")))
            
            try:
                if driver.find_elements(By.CLASS_NAME, "h2"):
                   name = driver.find_element(By.CLASS_NAME, "h2").text.strip() 
                else:
                    name = "N/A"
                if driver.find_elements(By.CLASS_NAME, "complete"):
                   address = driver.find_element(By.CLASS_NAME, "complete").text.strip()
                else:
                    address = "N/A"
                if driver.find_elements(By.CLASS_NAME, "contact-jump"):
                    contact = driver.find_element(By.CLASS_NAME, "contact-jump").text.strip() 
                else:
                    contact = "N/A"
                
                
                if name == "N/A" or address == "N/A" or contact == "N/A":
                    print(f"Skipping facility {i+1} due to missing data.")
                else:
                    print(f"Scraped: Name: {name}, Address: {address}, Contact: {contact}")
                    csvData.writerow([query, name, address, contact])
            except NoSuchElementException:
                print(f"Skipping facility {i+1} due to missing elements")


            driver.back()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#facility-cards-wrapper>tbody>tr>td>h3>a")))
        
        except (StaleElementReferenceException, TimeoutException) as e:
            print(f"Error with facility {i+1}: {e}")
            continue


driver.quit()
print("Scraping completed.")
