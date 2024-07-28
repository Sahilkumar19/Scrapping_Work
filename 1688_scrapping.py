import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scrape_1688_product(url):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "title-text"))
        )
        title = driver.find_element(By.CLASS_NAME, "title-text").text.strip()
    except Exception as e:
        title = "N/A"
        print(f"Title not found: {e}")

    try:
        image_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "detail-gallery-img"))
        )
        images = [img.get_attribute('src') for img in image_elements]
    except Exception as e:
        images = []
        print(f"Detail images not found: {e}")

    attributes = {}
    try:
        attribute_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "offer-attr-item"))
        )
        for elem in attribute_elements:
            key = elem.find_element(By.CLASS_NAME, "offer-attr-item-name").text.strip()
            value = elem.find_element(By.CLASS_NAME, "offer-attr-item-value").text.strip()
            attributes[key] = value
    except Exception as e:
        print(f"Attributes not found: {e}")

    desc_images = []
    try:
        desc_image_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "detail-description-content"))
        ).find_elements(By.CLASS_NAME, "desc-img-loaded")
        desc_images = [img.get_attribute('src') for img in desc_image_elements]
    except Exception as e:
        print(f"Description content not found: {e}")

    driver.quit()

    data = {
        "Title": [title],
        "Images": [", ".join(images)],
        "Attributes": [", ".join([f"{key}: {value}" for key, value in attributes.items()])],
        "Description Images": [", ".join(desc_images)]
    }

    df = pd.DataFrame(data)
    df.to_excel("1.xlsx", index=False, engine='openpyxl')

    print("Data saved to 1.xlsx")

product_url = "https://detail.1688.com/offer/746790811769.html?spm=a26352.13672862.offerlist.8.45d02cf5kvXNlp&cosite=-&tracelog=p4p&_p_isad=1&clickid=6132b9e638a84a829de0efc30b146aa7&sessionid=154bc9cc9a0069707b2cedd36b9dda85"
scrape_1688_product(product_url)