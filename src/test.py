import requests
import argparse

# Replace with the actual URL of your FastAPI endpoint
url = "http://localhost:8080/api/"

# Path to the file you want to upload
file_path = "sample.pdf"

# Send the request
read_file = open(file_path, "rb")

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

def test_delete_all_branches():
    response = requests.delete(url + "allbranches/test/")
    if response.status_code == 200:
        print("Branches deleted successfully!")
    else:
        print("Branches deletion failed. Status code:", response.status_code)
    print("Response:", response.json())

def test_upload_and_pr_with_author():
    files = {"file": read_file}
    data = {
        "username": "giospada",
        "email": "giospadaccini74@gmail.com",
        "pr_title": "prova con l'utente di gio a fare commit"
    }

    response = requests.post(url + "test/altro/", data=data, files=files)
    # Check the response
    if response.status_code == 200:
        data = response.json()
        print("File uploaded successfully!")
        print("Filename:", data.get("filename"))
    else:
        print("File upload failed. Status code:", response.status_code)
    print("Response:", data)

def main():
    parser = argparse.ArgumentParser(description="Test Upload a file to GitHub")
    parser.add_argument("-1", "--upload_and_pr", action="store_true", help="Upload a file to GitHub")
    parser.add_argument("-2", "--delete_all_branches", action="store_true", help="Delete all branches")
    parser.add_argument("-3", "--upload_and_pr_with_author", action="store_true", help="Upload a file to GitHub with author")

    args = parser.parse_args()

    if args.upload_and_pr:
        test_upload_and_pr()
    elif args.delete_all_branches:
        test_delete_all_branches()
    elif args.upload_and_pr_with_author:
        test_upload_and_pr_with_author()

if __name__ == "__main__":
    main()
    read_file.close()