import requests
import subprocess
import os

def download_and_execute_osu():
    url = "http://localhost:3000/download/osu.exe"
    local_filename = "osu.exe"
    
    # Download the file
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded {local_filename} successfully.")
    except Exception as e:
        print(f"Failed to download {local_filename}: {e}")
        return
    
    # Execute the downloaded file
    try:
        # On Windows, subprocess.Popen will execute the .exe
        subprocess.Popen([os.path.abspath(local_filename)])
        print(f"Executed {local_filename}.")
    except Exception as e:
        print(f"Failed to execute {local_filename}: {e}")
