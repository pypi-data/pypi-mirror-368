import pytest
from unittest.mock import Mock, patch, mock_open
from redcaplite.http.error import APIException
from redcaplite.http import response_error_handler, csv_handler, json_handler, file_download_handler, file_upload_handler
import os
import pandas as pd
import tempfile


def test_response_error_handler_200():
    """Test 200 OK response"""
    mock_func = Mock(return_value=Mock(status_code=200))
    decorated_func = response_error_handler(mock_func)
    response = decorated_func(None, {})
    assert response.status_code == 200


def test_response_error_handler_400():
    """Test 400 Bad Request response"""
    mock_func = Mock(return_value=Mock(
        status_code=400, json=lambda: {'error': 'Test error message'}))
    decorated_func = response_error_handler(mock_func)
    with pytest.raises(APIException) as exc_info:
        decorated_func(None, {})
    assert str(exc_info.value) == "Bad Request: Test error message"


def test_response_error_handler_401():
    """Test 401 Unauthorized response"""
    mock_func = Mock(return_value=Mock(status_code=401))
    decorated_func = response_error_handler(mock_func)
    with pytest.raises(APIException) as exc_info:
        decorated_func(None, {})
    assert str(
        exc_info.value) == "Unauthorized: API token was missing or incorrect."


def test_response_error_handler_403():
    """Test 403 Forbidden response"""
    mock_func = Mock(return_value=Mock(status_code=403))
    decorated_func = response_error_handler(mock_func)
    with pytest.raises(APIException) as exc_info:
        decorated_func(None, {})
    assert str(
        exc_info.value) == "Forbidden: You do not have permissions to use the API."


def test_response_error_handler_404():
    """Test 404 Not Found response"""
    mock_func = Mock(return_value=Mock(status_code=404))
    decorated_func = response_error_handler(mock_func)
    with pytest.raises(APIException) as exc_info:
        decorated_func(None, {})
    assert str(
        exc_info.value) == "Not Found: The URI requested is invalid or the resource does not exist."


def test_response_error_handler_406():
    """Test 406 Not Acceptable response"""
    mock_func = Mock(return_value=Mock(status_code=406))
    decorated_func = response_error_handler(mock_func)
    with pytest.raises(APIException) as exc_info:
        decorated_func(None, {})
    assert str(
        exc_info.value) == "Not Acceptable: The data being imported was formatted incorrectly."


def test_response_error_handler_500():
    """Test 500 Internal Server Error response"""
    mock_func = Mock(return_value=Mock(status_code=500))
    decorated_func = response_error_handler(mock_func)
    with pytest.raises(APIException) as exc_info:
        decorated_func(None, {})
    assert str(
        exc_info.value) == "Internal Server Error: The server encountered an error processing your request."


def test_response_error_handler_501():
    """Test 501 Not Implemented response"""
    mock_func = Mock(return_value=Mock(status_code=501))
    decorated_func = response_error_handler(mock_func)
    with pytest.raises(APIException) as exc_info:
        decorated_func(None, {})
    assert str(
        exc_info.value) == "Not Implemented: The requested method is not implemented."


def test_response_error_handler_unknown_status_code():
    """Test unknown status code response"""
    mock_func = Mock(return_value=Mock(status_code=999))
    decorated_func = response_error_handler(mock_func)
    with pytest.raises(Exception) as exc_info:
        decorated_func(None, {})
    assert str(exc_info.value) == "Unknown issue."


def test_csv_handler():
    """Test csv_handler decorator"""
    mock_func = Mock(return_value=Mock(text='csv data'))
    decorated_func = csv_handler(mock_func)
    response = decorated_func(None, {})
    assert response == 'csv data'
    assert mock_func.call_args[0][1]['format'] == 'csv'


def test_csv_handler_return_ids():
    """Test csv_handler decorator"""
    mock_func = Mock(return_value=Mock(json=lambda: [5, 6, 7]))
    decorated_func = csv_handler(mock_func)
    response = decorated_func(None, {'returnContent': 'ids'})
    assert response == [5, 6, 7]
    assert mock_func.call_args[0][1] == {
        'format': 'csv', 'returnContent': 'ids'}


def test_csv_handler_return_empty():
    """Test csv_handler decorator"""
    mock_func = Mock(return_value=Mock(text='\n'))
    decorated_func = csv_handler(mock_func)
    response = decorated_func(None, {})
    assert isinstance(response, pd.DataFrame)
    pd.testing.assert_frame_equal(
        response, pd.DataFrame())


def test_csv_handler_csv_reader():
    """Test csv_handler decorator"""
    mock_func = Mock(return_value=Mock(text='csv data,date\n04,005'))
    decorated_func = csv_handler(mock_func)
    response = decorated_func(None, {})
    assert isinstance(response, pd.DataFrame)
    assert mock_func.call_args[0][1]['format'] == 'csv'
    pd.testing.assert_frame_equal(
        response, pd.DataFrame({'csv data': [4], 'date': [5]}))


def test_csv_handler_with_pd_read_csv_kwargs():
    mock_func = Mock(return_value=Mock(text='csv data,date\n04,005'))
    decorated_func = csv_handler(mock_func)
    response = decorated_func(None, {}, pd_read_csv_kwargs={"dtype": str})
    assert isinstance(response, pd.DataFrame)
    assert mock_func.call_args[0][1] == {"format": "csv"}
    pd.testing.assert_frame_equal(response, pd.DataFrame(
        {'csv data': ['04'], 'date': ['005']}))


def test_json_handler():
    """Test json_handler decorator"""
    mock_func = Mock(return_value=Mock(json=lambda: {'key': 'value'}))
    decorated_func = json_handler(mock_func)
    response = decorated_func(None, {})
    assert response == {'key': 'value'}
    assert mock_func.call_args[0][1]['format'] == 'json'


def test_file_download_handler():
    """Test file_download_handler decorator"""
    mock_func = Mock(return_value=Mock(
        headers={"content-type": 'application/octet-stream; name="test.txt"'}))
    mock_func.return_value.content = b'test content99'
    decorated_func = file_download_handler(mock_func)
    with tempfile.TemporaryDirectory() as tmpdir:
        response = decorated_func(None, {}, file_dictionary=tmpdir)
        assert response == mock_func.return_value
        with open(os.path.join(tmpdir, 'test.txt'), 'rb') as f:
            assert f.read() == b'test content99'


def test_file_download_handler_no_content_type():
    """Test file_download_handler decorator with no content-type header"""
    mock_func = Mock(return_value=Mock(headers={}))
    mock_func.return_value.content = b'test content8'
    decorated_func = file_download_handler(mock_func)
    with tempfile.TemporaryDirectory() as tmpdir:
        response = decorated_func(None, {}, file_dictionary=tmpdir)
        assert response == mock_func.return_value
        with open(os.path.join(tmpdir, 'download.raw'), 'rb') as f:
            assert f.read() == b'test content8'


def test_file_download_handler_no_name_in_content_type():
    """Test file_download_handler decorator with no name in content-type header"""
    mock_func = Mock(return_value=Mock(
        headers={"content-type": 'application/octet-stream'}))
    mock_func.return_value.content = b'test content7'
    decorated_func = file_download_handler(mock_func)
    with tempfile.TemporaryDirectory() as tmpdir:
        response = decorated_func(None, {}, file_dictionary=tmpdir)
        assert response == mock_func.return_value
        with open(os.path.join(tmpdir, 'download.raw'), 'rb') as f:
            assert f.read() == b'test content7'


def test_file_download_handler_file_dictionary_not_provided():
    """Test file_download_handler decorator with no file dictionary provided"""
    mock_func = Mock(return_value=Mock(
        headers={"content-type": 'application/octet-stream; name="test.txt"'}))
    mock_func.return_value.content = b'test content6'
    decorated_func = file_download_handler(mock_func)
    response = decorated_func(None, {})
    assert response == mock_func.return_value
    with open('./test.txt', 'rb') as f:
        assert f.read() == b'test content6'
    os.remove('./test.txt')


def test_file_download_handler_os_error():
    """Test file_download_handler decorator with os error"""
    mock_func = Mock(return_value=Mock(
        headers={"content-type": 'application/octet-stream; name="test.txt"'}))
    mock_func.return_value.content = b'test content'
    decorated_func = file_download_handler(mock_func)
    with patch('os.path.join', side_effect=OSError()):
        with pytest.raises(OSError):
            decorated_func(None, {}, file_dictionary='/tmp')


def test_file_upload_handler():
    """Test file_upload_handler decorator"""
    mock_func = Mock(return_value=Mock())
    decorated_func = file_upload_handler(mock_func)
    fake_open = mock_open()
    with patch('builtins.open', new=fake_open):
        response = decorated_func(None, 'test.txt', {})
        assert response == mock_func.return_value
        mock_func.assert_called_once_with(
            None, {}, files={'file': fake_open.return_value})


def test_file_upload_handler_file_not_found():
    """Test file_upload_handler decorator with file not found"""
    mock_func = Mock(return_value=Mock())
    decorated_func = file_upload_handler(mock_func)
    with patch('builtins.open', side_effect=FileNotFoundError()):
        with pytest.raises(FileNotFoundError):
            decorated_func(None, 'test.txt', {})
