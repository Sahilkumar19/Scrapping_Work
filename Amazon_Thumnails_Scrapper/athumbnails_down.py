import csv
import os
import requests

def sanitize_filename(filename):
    # Remove invalid characters
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename

def download_image(url, save_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as out_file:
            out_file.write(response.content)
        print(f"Downloaded image to {save_path}")
    except requests.RequestException as e:
        print(f"Error downloading {url}. Error: {e}")

def main():
    csv_path = input("Enter the path to the CSV file (including the file name and extension, e.g., C:\\path\\to\\file.csv): ")
    save_directory = input("Enter the directory to save the images: ")

    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            product_link = row.get('ProductLink', '')
            base_name = os.path.basename(product_link).split('?')[0]
            
            for i in range(2, 9):  # Assuming there are Thumbnail_2 to Thumbnail_8 columns
                thumbnail_key = f'Thumbnail_{i}'
                thumbnail_url = row.get(thumbnail_key, '')
                if thumbnail_url:
                    sanitized_base_name = sanitize_filename(base_name)
                    filename = f"{sanitized_base_name}_thumb{i}.jpg"
                    save_path = os.path.join(save_directory, filename)
                    download_image(thumbnail_url, save_path)

if __name__ == "__main__":
    main()
