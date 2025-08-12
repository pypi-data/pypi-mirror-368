import os
from unittest.mock import Mock, patch, mock_open
from redcaplite.http import Client


def test_client_init():
    """Test Client initialization"""
    client = Client('https://example.com', 'token')
    assert client.url == 'https://example.com'
    assert client.token == 'token'


def test_client_post_json():
    """Test Client post method with JSON format"""
    client = Client('https://example.com', 'token')
    mock_response = Mock()
    with patch.object(client, '_Client__json_api', return_value=mock_response):
        response = client.post({'format': 'json'})
        assert response == mock_response


def test_client_post_csv():
    """Test Client post method with CSV format"""
    client = Client('https://example.com', 'token')
    mock_response = Mock()
    with patch.object(client, '_Client__csv_api', return_value=mock_response) as mock_csv_api:
        response = client.post({'format': 'csv'})
        assert response == mock_response
        mock_csv_api.assert_called_once_with(
            {'format': 'csv'}, pd_read_csv_kwargs={})

    with patch.object(client, '_Client__csv_api', return_value=mock_response) as mock_csv_api:
        response = client.post(
            {'format': 'csv'}, pd_read_csv_kwargs={"foo": []})
        assert response == mock_response
        mock_csv_api.assert_called_once_with(
            {'format': 'csv'}, pd_read_csv_kwargs={"foo": []})


def test_client_post_default_format():
    """Test Client post method with default format"""
    client = Client('https://example.com', 'token')
    mock_response = Mock()
    with patch.object(client, 'text_api', return_value=mock_response):
        response = client.post({})
        assert response == mock_response


def test_client__post():
    """Test Client _post method"""
    client = Client('https://example.com', 'token')
    mock_response = Mock()
    mock_response.status_code = 200
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client._Client__post({})
        assert response == mock_response
        mock_post.assert_called_once_with(
            'https://example.com', data={'token': 'token', 'returnFormat': 'json'}, files=None)


def test_client_file_download_api():
    """Test Client file_download_api method"""
    client = Client('https://example.com', 'token')
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b'test content'  # Specify the content attribute
    file_path = 'download.raw'
    with patch.object(client, '_Client__post', return_value=mock_response):
        response = client.file_download_api({})
        assert response == mock_response

    assert os.path.exists(file_path)
    with open(file_path, 'rb') as f:
        assert f.read() == mock_response.content
    os.remove(file_path)


def test_client_file_upload_api():
    """Test Client file_upload_api method"""
    client = Client('https://example.com', 'token')
    mock_response = Mock()
    with patch('builtins.open', new=mock_open(read_data=b'test content')) as mock_file:
        with patch.object(client, '_Client__post', return_value=mock_response):
            response = client.file_upload_api('file.txt', {})
            assert response == mock_response
            mock_file.assert_called_once_with('file.txt', 'rb')
