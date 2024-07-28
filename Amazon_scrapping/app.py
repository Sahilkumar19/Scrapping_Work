from flask import Flask, request, Response, render_template
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import unicodedata
import csv
import io

app = Flask(__name__)

def scrape_product(urls):
    all_products = []

    headers = {
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7"
    }

    for url in urls:
        o = {}
        specs_arr = []
        specs_obj = {}

        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"Failed to fetch page: {resp.status_code} for URL: {url}")
            continue

        soup = BeautifulSoup(resp.text, 'html.parser')
        
        o["url"] = url
        
        # Extract ASIN from URL
        parsed_url = urlparse(url)
        path_segments = parsed_url.path.split('/')
        asin = path_segments[-1] if path_segments[-1] != '' else path_segments[-2]
        o["asin"] = asin

        try:
            o["title"] = soup.find('h1', {'id': 'title'}).text.strip()
        except:
            o["title"] = None

        images = re.findall('"hiRes":"(.+?)"', resp.text)
        o["images"] = images

        try:
            o["price"] = soup.find("span", {"class": "a-price"}).find("span").text
        except:
            o["price"] = None

        try:
            o["rating"] = soup.find("i", {"class": "a-icon-star"}).text
        except:
            o["rating"] = None

        specs = soup.find_all("tr", {"class": "a-spacing-small"})

        for spec in specs:
            spanTags = spec.find_all("span")
            specs_obj[spanTags[0].text.strip()] = spanTags[1].text.strip()

        specs_arr.append(specs_obj)
        o["specs"] = specs_arr

        # Scrape technical details
        tech_details = {}
        table = soup.find('table', {'id': 'productDetails_techSpec_section_1'})
        if table:
            for row in table.find_all('tr'):
                key = row.find('th', {'class': 'a-color-secondary'}).text.strip()
                value = row.find('td', {'class': 'a-size-base'}).text.strip()
                value = value.replace('\u200e', '')
                value = unicodedata.normalize("NFKD", value)
                tech_details[key] = value
        o["technical_details"] = tech_details

        # Scrape about item section
        about_item = []
        about_item_section = soup.find('div', {'id': 'feature-bullets'})
        if about_item_section:
            for li in about_item_section.find_all('li', {'class': 'a-spacing-mini'}):
                about_item.append(li.text.strip())
        o["about_item"] = about_item

        # Scrape what's in the box section
        in_the_box = []
        witb_dl = soup.find('li', {'class': 'postpurchase-included-components-list-item'})
        if witb_dl:
            witb_items = witb_dl.find_all('span', {'class': 'a-list-item'})
            for item in witb_items:
                in_the_box.append(item.text.strip())
        o["whats_in_the_box"] = in_the_box

        # Scrape product description
        description = soup.find('div', {'id': 'productDescription'})
        if description:
            o["product_description"] = description.text.strip()
        else:
            o["product_description"] = ""
            
        additional_info = soup.find('div', {'id': 'productDetails_db_sections'})
        if additional_info:
            table = additional_info.find('table', {'id': 'productDetails_detailBullets_sections1'})
            if table:
                additional_data = {}
                for row in table.find_all('tr'):
                    th = row.find('th', {'class': 'a-color-secondary'})
                    td = row.find('td', {'class': 'a-size-base prodDetAttrValue'})
                    if th and td:
                        key = th.text.strip()
                        value = td.text.strip()
                        additional_data[key] = value
                o["additional_information"] = additional_data

        all_products.append(o)
    return all_products

def write_to_csv(data):
    keys = data[0].keys()
    output = io.StringIO()
    dict_writer = csv.DictWriter(output, keys)
    dict_writer.writeheader()
    dict_writer.writerows(data)
    output.seek(0)
    return output.getvalue()

@app.route('/', methods=['GET', 'POST'])
def amazon():
    if request.method == 'POST':
        urls = request.form['urls'].split()  # Split the input by whitespace to handle multiple URLs
        product_data = scrape_product(urls)
        if product_data:
            output_filename = "product_data.csv"
            csv_data = write_to_csv(product_data)
            return Response(
                csv_data,
                mimetype="text/csv",
                headers={"Content-disposition":
                         f"attachment; filename={output_filename}"}
            )
        else:
            return "Failed to fetch product data."
    return render_template('amazon.html')

if __name__ == '__main__':
    app.run(debug=True)
