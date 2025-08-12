# `redcaplite`

![pytest](https://github.com/jubilee2/RedcapLite/actions/workflows/python-app.yml/badge.svg?branch=main)
![PyPI - Version](https://img.shields.io/pypi/v/redcaplite)
![PyPI - Downloads](https://img.shields.io/pypi/dm/redcaplite)

`redcaplite` is a Python package designed for straightforward interaction with the REDCap (Research Electronic Data Capture) API. This package provides user-friendly methods to communicate with various API endpoints.

## Prerequisites
Before using `redcaplite`, you need to obtain two key pieces of information from your REDCap project's API page:
-   **API URL:** The web address (URL) for your REDCap API.
-   **API Token:** Your unique access token for authenticating API requests to your REDCap project.

## Installation

### From PyPI (Recommended)
To install `redcaplite` from the Python Package Index (PyPI), run the following command in your terminal:
```sh
pip install redcaplite
```
This is the recommended installation method for most users.

### From Source (for Development)
If you plan to contribute to `redcaplite` or require the latest development version, you can install it directly from the source code:
1.  Clone the repository:
    ```sh
    git clone https://github.com/jubilee2/RedcapLite.git
    ```
2.  Navigate to the cloned directory:
    ```sh
    cd RedcapLite
    ```
3.  Install the package in editable mode (this allows your changes to be immediately reflected):
    ```sh
    pip install -e .
    ```
This setup installs the package locally, making any modifications to the source code instantly available in your environment.

## Quick Start
Here's a quick example to get you started with `redcaplite`. This snippet demonstrates how to initialize the client and fetch basic project information.

```python
from redcaplite import RedcapClient

# Replace 'YOUR_REDCAP_API_URL' and 'YOUR_REDCAP_API_TOKEN' with your actual API URL and token.
API_URL = 'YOUR_REDCAP_API_URL'
API_TOKEN = 'YOUR_REDCAP_API_TOKEN'

# Create a RedcapClient instance
try:
    client = RedcapClient(API_URL, API_TOKEN)

    # Get basic project information
    project_info = client.get_project()
    print("Project Information:")
    if project_info: # project_info will be a dictionary on success
        print(f"  Project ID: {project_info.get('project_id')}")
        print(f"  Project Title: {project_info.get('project_title')}")
        print(f"  REDCap Version: {project_info.get('redcap_version')}")
    else:
        # This else block might be reached if the API returns an unexpected empty response
        # or if client.get_project() itself returns None on certain errors (check its implementation).
        print("Could not retrieve project information. The response was empty or unexpected.")
        print("Please verify your API URL, token, and project permissions.")

except Exception as e:
    print(f"An error occurred during API interaction: {e}")
    print("Please ensure your API URL and token are correct, the REDCap API is accessible, and your project has API permissions enabled.")

```

## Detailed Usage

### Importing the Package

To use `redcaplite` in your Python script, import the necessary components:

```python
import redcaplite # Or, more commonly:
# from redcaplite import RedcapClient
```

### Creating an Instance

Instantiate the `RedcapClient` class by providing your REDCap API URL and token:

```python
from redcaplite import RedcapClient

# Replace with your actual API URL and token
API_URL = 'YOUR_REDCAP_API_URL' # e.g., 'https://redcap.yourinstitution.org/api/'
API_TOKEN = 'YOUR_REDCAP_API_TOKEN' # e.g., 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

client = RedcapClient(API_URL, API_TOKEN)
# Now 'client' can be used to call various API methods.
# For example: project_details = client.get_project()
# It's good practice to wrap API calls in try-except blocks, as shown in the Quick Start section.
```

### Methods

The `RedcapClient` provides a wide range of methods to interact with the REDCap API. Here is a comprehensive list, categorized by typical REDCap actions (Export, Import, Delete). Not all actions are available for every API endpoint.

<details>
<summary>Click to expand/collapse the full list of API methods</summary>

| API Name | Export | Import | Delete |
|---|---|---|---|
| Arms | `get_arms()` | `import_arms()` | `delete_arms()` |
| DAGs | `get_dags()` | `import_dags()` | `delete_dags()` |
| User DAG Mapping | `get_user_dag_mappings()` | `import_user_dag_mappings()` |  |
| Events | `get_events()` | `import_events()` | `delete_events()` |
| Field Names | `get_field_names()` |  |  |
| File | `get_file()` | `import_file()` | `delete_file()` | 
| File Repository (File) | `export_file_repository()` | `import_file_repository()` | `delete_file_repository()` |
| File Repository (Folder)| `list_file_repository()` | `create_folder_file_repository()` |  | 
| Instrument | `get_instruments()` |  |  |
| Instrument (PDF)| `export_pdf()` |  |  |
| Form Event Mapping | `get_form_event_mappings()` | `import_form_event_mappings()` |  |
| Log | `get_logs()` |  |  |
| Metadata | `get_metadata()` | `import_metadata()` |  |
| Project | `get_project()`<br>`get_project_xml()` | `import_project_settings()` |  |
| Project (super user) |  | `create_project()` |  |
| Record | `export_records()`<br>`generate_next_record_name()` | `import_records()`<br>`rename_record()` | `delete_records()` |
| Repeating Forms Events | `get_repeating_forms_events()` | `import_repeating_forms_events()` |  |
| Report | `get_report()` |  |  |
| Version | `get_version()` |  |  |
| Survey | `get_survey_link()`<br>`get_survey_queue_link()`<br>`get_survey_return_code()`<br>`get_participant_list()` |  |  |
| Users | `get_users()` | `import_users()` | `delete_users()` |
| User Role | `get_user_roles()` | `import_user_roles()` | `delete_user_roles()` |
| User Role Mapping | `get_user_role_mappings()` | `import_user_role_mappings()` |  |

</details>

### Example

Here’s a complete example of how to use the `redcaplite` package:

```python
import redcaplite

# Create an instance of RedcapClient
r = redcaplite.RedcapClient('https://redcap.vumc.org/api/', 'your_token')

# Get arms
arms = r.get_arms()
print("Arms:", arms)

# Delete specific arms
r.delete_arms(arms=[3])
print("Arm 3 deleted successfully.")
```

### Advanced: Customizing CSV Exports with `pd_read_csv_kwargs`

When exporting data in CSV format using methods like `export_records()` or `get_report()`, `redcaplite` internally uses `pandas.read_csv()` to parse the initial response from REDCap. The `pd_read_csv_kwargs` parameter allows you to pass additional keyword arguments directly to `pandas.read_csv()`, giving you finer control over data type conversion and other parsing aspects.

#### Handling Data Types with `dtype`

A common use case for `pd_read_csv_kwargs` is to specify the data type of specific columns. For instance, to ensure a column like `participant_study_id` is treated as a string (preventing automatic conversion to a numeric type if it contains only digits), you can do the following:

```python
# When calling export_records or get_report
response = client.export_records(
    format='csv', 
    # ... other parameters ...
    pd_read_csv_kwargs={'dtype': {'participant_study_id': str}}
)
# Or for a specific report:
# report_data = client.get_report(
#     report_id='YOUR_REPORT_ID',
#     format='csv',
#     pd_read_csv_kwargs={'dtype': {'participant_study_id': str, 'another_id_field': str}}
# )

```

In this example, the `dtype` dictionary passed within `pd_read_csv_kwargs` instructs pandas to treat the `participant_study_id` column as `str` (string).

#### Benefits of using `pd_read_csv_kwargs`

-   **Preserve Data Integrity:** Ensure that sensitive data, like participant IDs, are maintained in their original string format, preventing unintended numeric conversions.
-   **Avoid Downstream Errors:** Prevent issues related to automatic data type conversions that might cause errors or unexpected behavior in subsequent data processing steps.
-   **Leverage Pandas Power:** Utilize pandas' robust data type handling capabilities to fine-tune your data parsing directly at the point of API interaction.

This feature is particularly useful for maintaining data consistency, especially for columns that might contain leading zeros or mixed alphanumeric characters but could be misinterpreted as numeric.

We hope this new feature helps you to work more efficiently and effectively with your REDCap data!

## Contributing

Contributions to `redcaplite` are welcome! If you would like to contribute, please fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
