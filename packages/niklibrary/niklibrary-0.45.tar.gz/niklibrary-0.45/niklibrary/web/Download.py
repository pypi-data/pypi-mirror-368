import os
import requests
from niklibrary.helper.Assets import Assets


class Download:

    @staticmethod
    def url(url):
        base_name = next((f1 for f1 in url.split('/') if f1.endswith('.zip')), None)
        output_file = os.getcwd() + os.path.sep + base_name
        if os.path.exists(output_file):
            print(f"{output_file} already exists")
            return
        print(f"Downloading {url} to {base_name}")
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 KB
        written_size = 0
        next_interval = 25

        with open(output_file, 'wb') as file:
            for data in response.iter_content(block_size):
                file.write(data)
                written_size += len(data)
                # Calculate the current progress percentage
                progress = (written_size / total_size) * 100
                if progress >= next_interval:
                    print(f"Downloaded {next_interval}% of the file...")
                    next_interval += 25

        print("Download complete.")
        return output_file