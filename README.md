# CSGITBOT

A github bot used to manage workflows in csunibo

## How to run

1. Create a .env file in the project root, follow `.env.example` schema
2. Install poetry, a python package manager, similar to npm
3. Run `poetry install`
4. Set the `config.ini` owner to correct owner repo, e.g. `csunibo`, or a user, you should have write and PR access to this
5. Serve the application with `poetry run start`
6. The application should be able to accept requests now.

# Features

## Automatic pull request

- You can specify a repo and a branch, and it automatically uploads a file and creates a PR on that repo!
- You can specify a commit author when creating a PR
- You can delete all the branches, except those defined in the config.