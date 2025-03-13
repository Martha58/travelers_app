from fastapi import FastAPI
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import time

app = FastAPI()

class SearchRequest(BaseModel):
    location: str
    checkin_date: str  
    checkout_date: str  

@app.post("/search_hotels")
def search_hotels(request: SearchRequest):
    options = options()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--start-maximized')
    options.add_argument('--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"')
    driver = webdriver.Chrome(options=options)

    # driver = webdriver.Edge()
    url = 'https://www.booking.com/'
    driver.get(url)

    links = set()
    hotel_name = []
    hotel_price = []
    hotel_rating = []
    review_count = []
    hotel_location = []
    hotel_facilities = []

    # Enter location
    location_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '(//input[contains(@name, "ss")])[1]'))
    )
    location_input.click()
    location_input.clear()
    location_input.send_keys(request.location)

    # Select check-in and check-out dates
    date_picker = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '(//div[contains(@class, "f73e6603bf")])[1]'))
    )
    date_picker.click()

    checkin_xpath = f'(//span[contains(@data-date, "{request.checkin_date}")])[1]'
    checkout_xpath = f'(//span[contains(@data-date, "{request.checkout_date}")])[1]'

    checkin_date = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, checkin_xpath))
    )
    driver.execute_script("arguments[0].click();", checkin_date)

    checkout_date = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, checkout_xpath))
    )
    checkout_date.click()

    # Click search button
    search_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '(//button[contains(@type, "submit")])[1]'))
    )
    search_button.click()

    # Dismiss sign-in popup if it appears
    try:
        signup_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[contains(@aria-label, "Dismiss sign-in info.")]'))
        )
        signup_button.click()
    except TimeoutException:
        pass

    # Scroll to load more hotels
    SCROLL_PAUSE_TIME = 3 
    scroll_count = 0 

    container = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'd4924c9e74')))
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        scroll_count += 1  
        print(f"Scrolling {scroll_count}...")  
        time.sleep(SCROLL_PAUSE_TIME)

        try:
            load_more = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "a83ed08757 c21c56c305 bf0537ecb5 ")]')))
            load_more.click()
            print("Clicked 'Load More' button.")  
            time.sleep(SCROLL_PAUSE_TIME)
        except TimeoutException:
            print("No more hotels to load.")
            break

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:  
            print("Reached the end of the page, stopping scrolling.")
            break
        last_height = new_height

    # Scroll back to the top before scraping
    print("Scrolling back to the top...")
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)

    # Extract hotel links
    hotels = WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'c066246e13.d8aec464ca'))
    )

    for hotel in hotels:
        try:
            name = hotel.find_element(By.XPATH, './/div[contains(@class, "d6767e681c")]').text
            print(f'Hotel name: {name}')
            hotel_name.append(name)
        except Exception as e:
            print(f"Error: {e}")
            hotel_name.append(None)

        try:
            price = hotel.find_element(By.XPATH, './/span[contains(@data-testid, "price-and-discounted-price")]').text
            print(f'Hotel price: {price}')
            hotel_price.append(price)
        except Exception as e:
            print(f"Error: {e}")
            hotel_price.append(None)

        try:
            link_element = hotel.find_element(By.XPATH, './/a[contains(@class, "a78ca197d0")]') 
            link = link_element.get_attribute('href')
            if link and "booking.com" in link and link not in links:
                links.add(link)
                print(f'Extracted link: {link}')
        except Exception as e:
            print(f"Error: {e}")
            
    links = list(links)

    for link in links[:5]:
        driver.get(link)
        time.sleep(2)   

        try:
            popup = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'map_full_overlay__close.js-map-modal-close')))
            driver.execute_script("arguments[0].click();", popup)
            print(f"Popup closed...")
        except Exception as e:
            print(f"No popup...")
        try:
            rating = driver.find_element(By.XPATH, '(//div[contains(@class, "ac4a7896c7")])[5]').text
        except Exception as e:
            rating = None
        try:
            reviews = driver.find_element(By.XPATH, '(//div[contains(@class, "dc5041d860")])[3]').text   
        except Exception as e:
            reviews = None
        try:
            location = driver.find_element(By.XPATH, './/div[contains(@data-testid, "PropertyHeaderAddressDesktop-wrapper")]').text
        except Exception as e:
            location = None
        try:
            facilities = driver.find_element(By.XPATH, '(.//ul[contains(@class, "c807d72881 d1a624a1cc e10711a42e")])[1]').text
        except Exception as e:
            facilities = None

        print(f"Rating: {rating}, Review: {reviews}, Location: {location}, Facilities: {facilities}")

        hotel_facilities.append(facilities)
        hotel_rating.append(rating)
        review_count.append(reviews)
        hotel_location.append(location)

    driver.quit()

    return {"location": request.location, "checkin_date": request.checkin_date, "checkout_date": request.checkout_date, "total_hotels": len(links), "hotel_links": list(links), "hotel_links": list(hotel_price), "hotel_name": list(hotel_name), "hotel_price": list(hotel_price), "hotel_facilities": list(hotel_facilities), "hotel_rating": list(hotel_rating), "hotel_location": list(hotel_location)}
