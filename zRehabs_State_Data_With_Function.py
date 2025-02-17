from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException


class State_Data_Scarp:
    def __init__(self, chrome_driver_path, csv_filename):
        self.chrome_driver_path = chrome_driver_path
        self.service = Service(self.chrome_driver_path)
        self.driver = webdriver.Chrome(service=self.service)
        self.driver.implicitly_wait(10) 
        self.csv_filename = csv_filename
        self.csvData = None

    def open_url(self, url):
        self.driver.get(url)
        print(f">>>>>>> {self.driver.title}")
        time.sleep(5)

    def csv_file(self):
        with open(self.csv_filename, 'w', newline ='', encoding ='utf_8') as file:
            self.csvData = csv.writer(file)
            self.csvData.writerow(['State_Name', 'Name', 'Address', 'Contact'])

    def get_state_link(self):
        try:
            return WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@id='top-states']//a"))
        )
        except TimeoutException:
            print("No, locate states list.")
            self.driver.quit()
            exit()
    
    def process_state_link(self, stateElement):
        stateName = stateElement.text
        state_url = stateElement.get_attribute("href")
        print(f"Processing State: {stateName}")

        self.driver.execute_script("window.open(arguments[0], '_blank');", state_url)
        self.driver.switch_to.window(self.driver.window_handles[1])

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#facility-cards-wrapper>tbody>tr>td>h3>a")))
            
        except TimeoutException:
                print(f"No facility found for {stateName}")
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                return
        
        facility_count = len(self.driver.find_elements(By.CSS_SELECTOR, "#facility-cards-wrapper>tbody>tr>td>h3>a"))
        print(f"{facility_count} facilities found in {stateName}.")
        
        for i in range(facility_count):

            self.get_facility_link(stateName, i)

        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
    
    def get_facility_link(self, stateName, i):
        try:
            facilityLinks = self.driver.find_elements(By.CSS_SELECTOR, "#facility-cards-wrapper>tbody>tr>td>h3>a")
                    
            if i >= len(facilityLinks):
                return
                    
            facilityLink = facilityLinks[i]
            self.driver.execute_script("arguments[0].scrollIntoView(true);", facilityLink)
            time.sleep(2)
            self.driver.execute_script("arguments[0].click();", facilityLink)

            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "outline")))

            name, address, contact = self.get_facility_details()

            print(f"Scraped: Name: {name}, Address: {address}, Contact: {contact}")

            with open(self.csv_filename, 'a', newline='', encoding='utf-8') as file:
                self.csvData = csv.writer(file)
                self.csvData.writerow([stateName, name, address, contact])
        

            self.driver.execute_script("window.history.go(-1)")

            WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#facility-cards-wrapper>tbody>tr>td>h3>a")))
            
        except (StaleElementReferenceException, TimeoutException) as e:
            print(f"Error with facility {i+1}: {e}")

    def get_facility_details(self):
        try:
            name = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "h2"))
            ).text
            address = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "complete"))
            ).text
            contact = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "contact-jump"))
            ).text
            return name, address, contact
        except NoSuchElementException:
            print(f"Not find all details for")
            return
        
    def scraping(self, url):
        self.open_url(url)
        self.csv_file()
        stateElements = self.get_state_link()
        print(f"{len(stateElements)} States found.")

        for stateElement in stateElements:
            self.process_state_link(stateElement)

        self.driver.quit()
        print("Scraping completed.")


chrome_driver_path = "chromedriver-win64/chromedriver.exe"
url = "https://rehabs.org"
csv_filename = "new/zNewtab2_With_Function.csv"

fd = State_Data_Scarp(chrome_driver_path, csv_filename)
fd.scraping(url)