import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urlparse
from datetime import datetime

def scrape_industrybuying_product(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check if the request was successful
    except requests.exceptions.HTTPError as http_err:
        print(f"An error occurred while scraping {url}: {http_err}")  # Handle HTTP errors
        return None
    except Exception as err:
        print(f"An error occurred while scraping {url}: {err}")  # Handle other errors
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    product_data = {}

    # Product Title
    product_title_elem = soup.find('span', class_='productTitle')
    if product_title_elem and product_title_elem.find('h1'):
        product_title = product_title_elem.find('h1').get_text(strip=True)
        product_data['Title'] = product_title
    else:
        product_data['Title'] = None

    # Price
    price_elem = soup.find('span', class_='AH_PricePerPiece')
    if price_elem:
        price = price_elem.get_text(strip=True)
        product_data['Price'] = price
    else:
        product_data['Price'] = None

    # Features
    features_table = soup.find('tbody')
    if features_table:
        features = {}
        for row in features_table.find_all('tr'):
            columns = row.find_all('td')
            if len(columns) == 2:
                feature_name = columns[0].get_text(strip=True).replace(" :", "")
                feature_value = columns[1].get_text(strip=True)
                features[feature_name] = feature_value
        product_data['Features'] = features
    else:
        product_data['Features'] = None

    # Detailed Description
    description_section = soup.find('div', id='description')
    if description_section:
        description = ' '.join(p.get_text(strip=True) for p in description_section.find_all('p'))
        product_data['Description'] = description
    else:
        product_data['Description'] = None

    # Product Image
    image_elem = soup.find('a', class_='AH_MultipleImageList')
    if image_elem and image_elem.find('img'):
        image_url = image_elem.find('img')['data-zoom-image']
        product_data['Image URL'] = f"https:{image_url}"
    else:
        product_data['Image URL'] = None

    # Additional Specifications
    specifications = {}
    specifications_container = soup.find('div', id='famSpec')
    if specifications_container:
        for spec in specifications_container.find_all('div', class_='filterRow'):
            feature_name = spec.find('div', class_='featureNamePr').get_text(strip=True)
            feature_value = spec.find('div', class_='featureValuePr').get_text(strip=True).replace(": ", "")
            specifications[feature_name] = feature_value
        product_data['Specifications'] = specifications
    else:
        product_data['Specifications'] = None

    return product_data

def read_csv(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        urls = [row[0] for row in reader if row]  # Ensure the row is not empty
    return urls

def write_csv(data):
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_csv = f"output_{now}.csv"
    headers = ["Title", "Price", "Description", "Image URL", "Features", "Specifications"]
    with open(output_csv, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for row in data:
            writer.writerow([
                # row.get("URL"),
                row.get("Title"),
                row.get("Price"),
                row.get("Description"),
                row.get("Image URL"),
                row.get("Features"),
                row.get("Specifications")
            ])
    print(f"Output CSV file '{output_csv}' created successfully.")

def is_valid_url(url):
    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc])

def main(input_csv):
    urls = read_csv(input_csv)
    product_details = []

    for url in urls:
        if is_valid_url(url):
            data = scrape_industrybuying_product(url)
            if data:
                data["URL"] = url
                product_details.append(data)
        else:
            print(f"Invalid URL: {url}")

    if product_details:
        write_csv(product_details)

if __name__ == "__main__":
    input_csv = 'input.csv'
    main(input_csv)
