import requests

# Replace with the actual URL of your FastAPI endpoint
url = "http://localhost:8080/api/"

# Path to the file you want to upload
file_path = "sample.pdf"

# Send the request
with open(file_path, "rb") as file:
    read_file = file.read()

def test_upload_and_pr():

    files = {"file": read_file}
    response = requests.post(url + "test/prova/", files=files)
    # Check the response
    if response.status_code == 200:
        data = response.json()
        print("File uploaded successfully!")
        print("Filename:", data.get("filename"))
    else:
        print("File upload failed. Status code:", response.status_code)
    print("Response:", data)

# test_upload_and_pr()

def test_delete_all_branches():
    response = requests.delete(url + "allbranches/test/")
    if response.status_code == 200:
        print("Branches deleted successfully!")
    else:
        print("Branches deletion failed. Status code:", response.status_code)
    print("Response:", response.json())

test_delete_all_branches()