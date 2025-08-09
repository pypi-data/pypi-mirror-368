import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import httpx
import schedule

DATA_FILE = "last_scrape.json"

driver = None

class Ntfy:
    def __init__(self, url, priority="default", tags="bell"):
        self.url = url
        self.priority = priority
        self.tags = tags
        
    def notify(self, message):
        headers = {
            "Priority": str(self.priority),
            "Tags": self.tags
        }
        print(f"Sending notification: {message}")
        httpx.post(self.url, data=message.encode("utf-8"), headers=headers)

class PriceScraper:
    def __init__(self, url, selectors, name, notifier):
        self.url = url
        self.selectors = selectors if isinstance(selectors, list) else [selectors]
        self.name = name
        self.notifier = notifier
        self.last_price = None
        self.load_last_price()
        
    def load_last_price(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    if self.url in data:
                        self.last_price = data[self.url]
                        print(f"Loaded last price for {self.name}: {self.last_price}")
            except Exception as e:
                print(f"Error loading last price: {e}")
                
    def save_last_price(self):
        data = {}
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
            except:
                pass
        
        data[self.url] = self.last_price
        
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)
            
    def scrape(self):
        print(f"Scraping {self.name}...")
        driver.get(self.url)
        time.sleep(5)
        
        current_price = None
        for selector in self.selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                current_price = element.text.strip()
                print(f"Found price with selector {selector}: {current_price}")
                break
            except NoSuchElementException:
                continue
        
        if not current_price:
            self.notifier.notify(f"Could not find price for {self.name}")
            return
            
        if self.last_price is None:
            self.notifier.notify(f"First check for {self.name}: {current_price}")
        elif current_price != self.last_price:
            self.notifier.notify(f"Price changed for {self.name} from {self.last_price} to {current_price}")
        else:
            print(f"Price unchanged for {self.name}: {current_price}")
            
        self.last_price = current_price
        self.save_last_price()

def setup_driver():
    global driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def main():
    setup_driver()
    
    ntfy_notifier = Ntfy(
        url="https://ntfy.sh/games", # Use your topic
        priority=3,
        tags="bell",
    )
    
    scrapers = [
        # Add scrapers as needed
        # Example:
        PriceScraper(
            url="https://store.steampowered.com/app/1623730/Palworld/",
            selectors=["div.discount_final_price", "div.game_purchase_price.price"], # These are the CSS selectors for the price elements for steam
            name="Palworld",
            notifier=ntfy_notifier
        )
    ]
    
    def run_all_scrapers():
        for scraper in scrapers:
            try:
                scraper.scrape()
            except Exception as e:
                print(f"Error scraping {scraper.name}: {e}")
            time.sleep(5)
    
    try:
        run_all_scrapers()
        
        schedule.every(24).hours.do(run_all_scrapers) # Runs every 24 hours
        
        print("Scraper running.")
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Stopping scraper...")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()