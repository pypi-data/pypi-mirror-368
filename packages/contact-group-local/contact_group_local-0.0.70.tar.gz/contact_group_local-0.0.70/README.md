# python-package-template  

This repository is designed to help you create local and remote package layers in Python.  
It focuses on building package layers and does not include GraphQL and REST-API layers.

## Download Environment

To set up the environment, follow these steps in your terminal:

```shell
git clone https://github.com/circles-zone/<your-repo>.git --branch dev  # or other branch
cd <your-repo>
git checkout -b BU-<new-branch>  # if a new branch is needed
python -m venv venv
pip install -r requirements.txt
... <edit your code> ...
git add .
git commit -m "Your commit message"
git push origin BU-<your-branch>
```

For more detailed information, refer to
the [documentation](https://docs.google.com/document/d/1HKhwlhwLD3S8uJ9LPI7h4Nxu77-DXKZe/edit?usp=sharing&ouid=104468990154530891864&rtpof=true&sd=true).

## Check List:

### Directory Structure

Ensure that the root directory has the following structure:

- `.github/`
- `.vscode/` (optional)
- `directory_with_same_name_as_the_repo/`
    - `db/`
    - `reports/`
    - `project_name/`
        - `src/`
            - `__init__.py`
            - `example_class.py`
        - `tests/`
            - `example_class_test.py`
        - `__init__.py`

This setup enables easy switching to a mono repo configuration.

### Database Python Scripts

Place `<table-name>.py` in the `/db` folder if needed.  
There's no need for a separate file for `_ml` tables.  
Feel free to delete the example file if it's not required.

### Database Schema and Data

- Create files to define the database schema, tables, views, and populate metadata and test data.
- Use `/db/<table-name>.py` to create the schema, tables, views (including `_ml_table`).
- Use `/db/<table-name>_insert.py` to create metadata and test data records.

### Update `setup.py`

Don't forget to update the `setup.py` file, including the package name and version.  
Remember to upload the version after every deployment.

### Working with VS Code

Ensure that you push the `launch.json` file to the repository.  
This enables running and debugging the code smoothly.

### Unit Testing

We recommend using `pytest` over the `unittest` package.  
Create a `pytest.ini` file in the project directory, not the root directory.
run in termianl: pytest

## Workflow Completion

When you've addressed all the TODOs in the repository, using infrastructure classes like Logger, Database, Url,
Importer, and others, make sure your Feature Branch GitHub Actions Workflow is green without warnings.  
All tests should run in GitHub Actions, your code should be well-documented, the `README.md` file should be clear and
self-explanatory, test coverage should be above 90%, and all lines of code should be covered by unit tests.

Once these conditions are met, you can filter and analyze your records in Logz.io.  
Pull the `dev` branch to your Feature Branch and then create a Pull Request to `dev`.

Good luck :)

## check your code visibility lint with flake (Mandatory before pusj):

run those command
python -m pip install flake8 pytest
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

note: you should use autopep8 extension in your code!
