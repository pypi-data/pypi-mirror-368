import requests
import redcaplite.http.handler as hd


class Client:
    def __init__(self, url, token):
        self.url = url
        self.token = token

    def post(self, data, pd_read_csv_kwargs={}):
        format = data.get("format", None)
        if format == 'csv':
            response = self.__csv_api(
                data, pd_read_csv_kwargs=pd_read_csv_kwargs)
        elif format == 'json':
            response = self.__json_api(data)
        elif format == 'xml':
            response = self.text_api(data)
        else:
            response = self.text_api(data)
        return response

    @hd.response_error_handler
    def __post(self, data, files=None):
        data['token'] = self.token
        response = requests.post(self.url, data=data, files=files)
        print('HTTP Status: ' + str(response.status_code))
        return response

    @hd.csv_handler
    def __csv_api(self, data):
        return self.__post(data)

    @hd.json_handler
    def __json_api(self, data):
        return self.__post(data)

    @hd.text_handler
    def text_api(self, data):
        return self.__post(data)

    @hd.file_download_handler
    def file_download_api(self, data):
        return self.__post(data)

    @hd.file_upload_handler
    def file_upload_api(self, data, files):
        return self.__post(data, files=files)
