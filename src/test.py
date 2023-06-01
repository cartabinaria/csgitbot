import requests

# Replace with the actual URL of your FastAPI endpoint
url = "http://localhost:8000/upload_file/"

# Path to the file you want to upload
file_path = "path/to/file.pdf"

# Send the request
with open(file_path, "rb") as file:
    files = {"file": file}
    response = requests.post(url, files=files)

# Check the response
if response.status_code == 200:
    data = response.json()
    print("File uploaded successfully!")
    print("Filename:", data.get("filename"))
else:
    print("File upload failed. Status code:", response.status_code)
