from github import Github
import base64

# Replace with your bot's access token
access_token = ""

# Replace with the repository details
repository_owner = "flecart"
repository_name = "test"

# Replace with the branch name you want to create
new_branch_name = "NEW_BRANCH_NAME"

# Connect to GitHub using the access token
g = Github(access_token)

# Get the repository
repo = g.get_repo(f"{repository_owner}/{repository_name}")

# Create the new branch
# base_branch = repo.get_branch("main")  # Replace with the base branch name
# new_branch = repo.create_git_ref(f"refs/heads/{new_branch_name}", base_branch.commit.sha)
# print(f"Created branch: {new_branch_name}")

try:
    # Get the repository
    repo = g.get_repo(f"{repository_owner}/{repository_name}")

    # Create a new file
    file_path = "new_file.pdf"

    file_path = "sample.pdf"
    with open(file_path, "rb") as file:
        file_content = file.read()

    branch = repo.get_branch(new_branch_name)
    new_file = repo.create_file(file_path, "New file created", file_content, new_branch_name)

    print(f"New file created: {new_file}")
except Exception as e:
    print(f"Error occurred: {str(e)}")