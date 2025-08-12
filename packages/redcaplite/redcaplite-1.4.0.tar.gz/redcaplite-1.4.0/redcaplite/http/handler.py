from .error import APIException
import os
import io
import pandas as pd


def response_error_handler(func):
    def wrapper(obj, data, files=None):
        data['returnFormat'] = 'json'
        response = func(obj, data, files=files)
        if response.status_code == 200:
            return response
        elif response.status_code == 400:
            raise APIException(
                f"Bad Request: {response.json().get('error', 'No message provided')}")
        elif response.status_code == 401:
            raise APIException(
                "Unauthorized: API token was missing or incorrect.")
        elif response.status_code == 403:
            raise APIException(
                "Forbidden: You do not have permissions to use the API.")
        elif response.status_code == 404:
            raise APIException(
                "Not Found: The URI requested is invalid or the resource does not exist.")
        elif response.status_code == 406:
            raise APIException(
                "Not Acceptable: The data being imported was formatted incorrectly.")
        elif response.status_code == 500:
            raise APIException(
                "Internal Server Error: The server encountered an error processing your request.")
        elif response.status_code == 501:
            raise APIException(
                "Not Implemented: The requested method is not implemented.")
        else:
            raise Exception("Unknown issue.")
    return wrapper


def csv_handler(func):
    def wrapper(obj, data, pd_read_csv_kwargs={}):
        data['format'] = 'csv'
        response = func(obj, data)
        if 'returnContent' in data and data['returnContent'] == 'ids':
            return response.json()
        if response.text.strip() == '':
            return pd.DataFrame()  # Return an empty DataFrame if response is empty
        io_string = io.StringIO(response.text)
        df = pd.read_csv(io_string, **pd_read_csv_kwargs)
        io_string.close()
        if df.shape == (0, 1):
            return response.text
        return df
    return wrapper


def json_handler(func):
    def wrapper(obj, data):
        data['format'] = 'json'
        response = func(obj, data)
        return response.json()
    return wrapper


def text_handler(func):
    def wrapper(obj, data):
        response = func(obj, data)
        return response.text
    return wrapper


def file_download_handler(func):
    def wrapper(obj, data, file_dictionary=''):
        response = func(obj, data)
        try:
            # Extract and clean the content-type header, splitting by semicolon
            # and stripping spaces
            content_type = response.headers["content-type"]
            splat = [item.strip() for item in content_type.split(";")]

            # Create a dictionary of key-value pairs from the cleaned
            # content-type
            content_dict = {
                key: value.replace('"', "")
                for item in splat
                if "=" in item
                for key, value in [item.split("=")]
            }
            file_name = content_dict['name']

        except:  # noqa: E722
            file_name = 'download.raw'

        with open(os.path.join(file_dictionary, file_name), 'wb') as f:
            f.write(response.content)
        return response
    return wrapper


def file_upload_handler(func):
    def wrapper(obj, file_path, data):
        with open(file_path, 'rb') as file_obj:
            response = func(obj, data, files={'file': file_obj})
        return response
    return wrapper
