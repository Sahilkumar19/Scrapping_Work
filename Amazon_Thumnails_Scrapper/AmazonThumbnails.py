import pandas as pd
import requests
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def fetch_product_thumbnails(product_url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    driver.get(product_url)
    
    thumbnail_urls = []
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#altImages ul li img'))
        )
        
        # Find product thumbnail image elements
        img_tags = driver.find_elements(By.CSS_SELECTOR, '#altImages ul li img')
        
        for img_tag in img_tags:
            img_url = img_tag.get_attribute('src')
            
            if img_url and 'data:image/' not in img_url:
                img_url = img_url.replace('_SS40_', '_SL1500_')
                thumbnail_urls.append(img_url)
    
    except Exception as e:
        print(f"Thumbnail not found for {product_url}: {e}")
    
    finally:
        driver.quit()
    
    return thumbnail_urls

def save_thumbnails_to_csv(csv_file, output_csv):
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' does not exist.")
        return
    
    df = pd.read_csv(csv_file)
    
    if df.empty:
        print(f"Error: CSV file '{csv_file}' is empty.")
        return
    
    if 'ProductLink' not in df.columns:
        raise ValueError("CSV file must contain 'ProductLink' column")
    
    data = []
    
    for product_url in df['ProductLink']:
        thumbnails = fetch_product_thumbnails(product_url)
        if thumbnails:
            # Exclude the first thumbnail and include the rest
            thumbnails = thumbnails[1:]
            if thumbnails:
                # Create a row with the product URL followed by its thumbnails
                row = [product_url] + thumbnails
                data.append(row)
            else:
                # Create a row with the product URL followed by a message if no thumbnails are found
                data.append([product_url, 'No thumbnails found'])
        else:
            # Create a row with the product URL followed by a message if no thumbnails are found
            data.append([product_url, 'No thumbnails found'])
    
    max_thumbnails = max(len(row) - 1 for row in data)
    columns = ['ProductLink'] + [f'Thumbnail_{i+2}' for i in range(max_thumbnails)]  # Start from Thumbnail_2
    
    thumbnails_df = pd.DataFrame(data, columns=columns)
    thumbnails_df.to_csv(output_csv, index=False)


csv_file = 'at60.csv'
output_csv = 'at60_op.csv'
save_thumbnails_to_csv(csv_file, output_csv)