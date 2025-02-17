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

# Step 1: Open Website
driver.get("https://rehabs.org")
print(f">>>>>>> {driver.title}")

time.sleep(5)

csv_filename = 'new/4_zzz.csv'
with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
    csvData = csv.writer(file)
    csvData.writerow(['State_Name','Name', 'Address', 'Contact'])

    try:
        stateElements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@id='top-states']//a"))
        )
    except TimeoutException:
        print("No, locate states list.")
        driver.quit()
        exit()

    print(f"{len(stateElements)} States found.")

    for stateElement in stateElements:
        try:
            stateName = stateElement.text
            state_url = stateElement.get_attribute("href")
            print(f"Processing State: {stateName}")

            driver.execute_script("window.open(arguments[0], '_blank');", state_url)
            driver.switch_to.window(driver.window_handles[1])

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#facility-cards-wrapper>tbody>tr>td>h3>a"))
                )
            except TimeoutException:
                print(f"No facility found for {stateName}")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue

            facility_count = len(driver.find_elements(By.CSS_SELECTOR, "#facility-cards-wrapper>tbody>tr>td>h3>a"))
            print(f"{facility_count} facilities found in {stateName}.")

            for i in range(facility_count):
                try:
            
                    facilityLinks = driver.find_elements(By.CSS_SELECTOR, "#facility-cards-wrapper>tbody>tr>td>h3>a")
                    
                    if i >= len(facilityLinks):
                        break
                    
                    facilityLink = facilityLinks[i]
                    driver.execute_script("arguments[0].scrollIntoView(true);", facilityLink)
                    time.sleep(2)
                    driver.execute_script("arguments[0].click();", facilityLink)

                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "outline"))
                    )

                    try:
                        name = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "h2"))
                        ).text
                        address = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "complete"))
                        ).text
                        contact = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "contact-jump"))
                        ).text

                        print(f"Scraped: Name: {name}, Address: {address}, Contact: {contact}")
                        csvData.writerow([stateName, name, address, contact])

                    except NoSuchElementException:
                        print(f"Not find all details for {facilityLink}")

                    driver.execute_script("window.history.go(-1)")

                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#facility-cards-wrapper>tbody>tr>td>h3>a"))
                    )

                except (StaleElementReferenceException, TimeoutException) as e:
                    print(f"Error with facility {i+1}: {e}")
                    continue

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        except Exception as e:
            print(f"Error processing state {stateName}: {e}")
            driver.switch_to.window(driver.window_handles[0])
            continue

driver.quit()
print("Scraping completed.")
