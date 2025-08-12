import os
import requests
from bs4 import BeautifulSoup
import re
from collections import defaultdict
from datetime import datetime


class OemOp:

    @staticmethod
    def write_all_files(dir_path, overwrite=True):
        all_files_path = dir_path + os.path.sep + "all_files.txt"
        if overwrite or not os.path.exists(all_files_path):
            with open(all_files_path, "w") as f:
                directory = str(dir_path)
                # Walk through the directory and list files
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        # Write the relative file path to the file
                        relative_path = os.path.relpath(os.path.join(root, file), directory)
                        f.write(relative_path.replace("\\", "/") + '\n')
        else:
            print("All files already written")

    @staticmethod
    def get_latest_ota_url(device_name, android_version=None):
        url = "https://developers.google.com/android/ota"
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        try:
            response = requests.get(url, cookies={"devsite_wall_acks": "nexus-ota-tos"}, headers=header)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")
        except Exception as e:
            print(f"Failed to fetch the page. Error: {str(e)}")
            return None
        soup = BeautifulSoup(response.content, 'html.parser')

        device_section = soup.find(id=device_name)
        if not device_section:
            raise Exception(f"Device {device_name} not found on the page.")

        # Find the table next to the device section
        table = device_section.find_next('table')
        if not table:
            raise Exception(f"No table found for device {device_name}.")

        # Initialize a dictionary to categorize URLs
        categorized_urls = defaultdict(list)

        # Find all rows in the table
        rows = table.find_all('tr')[1:]  # Skip the header row

        for row in rows:
            columns = row.find_all('td')
            if len(columns) < 3:
                continue

            version_info = columns[0].get_text(strip=True)
            link = columns[1].find('a', href=True)['href']
            checksum = columns[2].get_text(strip=True)

            # Extract the month and year from the version_info
            match = re.search(r'\((.*?)\)', version_info)
            if match:
                date_info = match.group(1).split(',')[1].strip()
                date = datetime.strptime(date_info, '%b %Y')
                category = "Regular"
                if 'T-Mobile' in version_info:
                    category = 'T-Mobile'
                elif 'Verizon' in version_info:
                    category = 'Verizon'
                elif 'G-store' in version_info:
                    category = 'G-store'
                categorized_urls[date].append({
                    'url': link,
                    'checksum': checksum,
                    'category': category,
                    'version_info': version_info
                })

        # Sort the categorized URLs by date
        sorted_dates = sorted(categorized_urls.keys(), reverse=True)

        # Find the latest regular build
        latest_regular_url = None
        for date in sorted_dates:
            for url_info in categorized_urls[date]:
                if url_info['category'] == 'Regular':
                    if android_version and f"{android_version}.0.0" not in url_info['version_info']:
                        continue
                    latest_regular_url = url_info['url']
                    break
            if latest_regular_url:
                break

        if not latest_regular_url:
            raise Exception(f"No valid regular OTA URLs found for device {device_name}.")

        return latest_regular_url
