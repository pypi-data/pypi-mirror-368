"""
A JSON-oriented API client using only Python standard library.
"""
from __future__ import annotations

import json
import logging
import re
import ssl
from http.client import HTTPResponse
from io import IOBase
from typing import Any, Mapping, MutableMapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from zut import get_logger

class ApiClient:
    """
    A JSON API client using only Python standard library.
    """

    base_url : str|None = None
    timeout: float|None = None
    """ Timeout in seconds. """

    force_trailing_slash: bool = False

    default_headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json; charset=utf-8',
    }

    json_encoder_cls: type[json.JSONEncoder]|None = None
    json_decoder_cls: type[json.JSONDecoder] = json.JSONDecoder
    
    print_error_maxlen = 400

    no_ssl_verify = False


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # necessary to allow this class to be used as a mixin
        self._logger = get_logger(type(self).__module__ + '.' + type(self).__name__)
        self._ssl_context = None
        if self.no_ssl_verify or kwargs.get('no_ssl_verify'):
            self._ssl_context = ssl.create_default_context()
            self._ssl_context.check_hostname = False
            self._ssl_context.verify_mode = ssl.CERT_NONE

        if not self.__class__.json_encoder_cls:            
            from zut.json import ExtendedJSONEncoder
            self.__class__.json_encoder_cls = ExtendedJSONEncoder


    def __enter__(self):
        return self


    def __exit__(self, exc_type = None, exc_value = None, exc_traceback = None):
        pass


    def get(self, endpoint: str|None = None, *, params: Mapping|None = None, headers: MutableMapping[str,str]|None = None):
        return self.request(endpoint, method='GET', params=params, headers=headers)


    def post(self, endpoint: str|None = None, data = None, *, params: Mapping|None = None, headers: MutableMapping[str,str]|None = None, content_type: str|None = None, content_length: int|None = None, content_filename: str |None= None):
        return self.request(endpoint, data, method='POST', params=params, headers=headers, content_type=content_type, content_length=content_length, content_filename=content_filename)
    

    def put(self, endpoint: str|None = None, data = None, *, params: Mapping|None = None, headers: MutableMapping[str,str]|None = None, content_type: str|None = None, content_length: int|None = None, content_filename: str |None= None):
        return self.request(endpoint, data, method='PUT', params=params, headers=headers, content_type=content_type, content_length=content_length, content_filename=content_filename)
   

    def request(self, endpoint: str|None = None, data = None, *, method = None, params: Mapping|None = None, headers: MutableMapping[str,str]|None = None, content_type: str|None = None, content_length: int|None = None, content_filename: str|None = None) -> dict[str,Any]:
        url = self.prepare_url(endpoint, params=params)

        all_headers = self.get_request_headers(url)
        if headers:
            for key, value in headers.items():
                all_headers[key] = value
                if key == 'Content-Type' and not content_type:
                    content_type = value
                elif key == 'Content-Length' and content_length is None:
                    content_length = int(value) if isinstance(value, str) else value
                elif key == 'Content-Disposition' and not content_filename:
                    m = re.search(r'attachment\s*;\s*filename\s*=\s*(.+)', value)
                    if m:
                        content_filename = m[1].strip()

        if content_type:
            all_headers['Content-Type'] = content_type
        if content_length is not None:
            all_headers['Content-Length'] = str(content_length)
        if content_filename:
            all_headers['Content-Disposition'] = f"attachment; filename={content_filename}"
                
        if data is not None:
            if not method:
                method = 'POST'

            if isinstance(data, IOBase) or (content_type and not 'application/json' in content_type):
                # keep data as is: this is supposed to be an uploaded file
                if not content_type:
                    content_type = 'application/octet-stream'
            else:
                data = json.dumps(data, ensure_ascii=False, cls=self.json_encoder_cls).encode('utf-8')
            
            self._logger.debug('%s %s', method, url)
            request = Request(url,
                method=method,
                headers=all_headers,
                data=data,
            )
        else:
            if not method:
                method = 'GET'
            
            self._logger.debug('%s %s', method, url)
            request = Request(url,
                method=method,
                headers=all_headers,
            )

        try:
            response: HTTPResponse
            with urlopen(request, timeout=self.timeout, context=self._ssl_context) as response:
                if self._logger.isEnabledFor(logging.DEBUG):
                    content_type = response.headers.get('content-type', '-')
                    self._logger.debug('%s %s %s %s', response.status, url, response.length, content_type)
                return self.get_dict_response(response)
            
        except HTTPError as error:
            with error:
                http_data = self.get_dict_or_str_response(error)
            raise ApiClientError(error, http_data, message_maxlen=self.print_error_maxlen) from None

        except Exception as error:
            raise ApiClientError(error, message_maxlen=self.print_error_maxlen) from None


    def prepare_url(self, endpoint: str|None, *, params: Mapping|None = None, base_url: str|None = None):
        if endpoint is None:
            endpoint = ''

        if not base_url and self.base_url:
            base_url = self.base_url

        if '://' in endpoint or not base_url:
            url = endpoint
            
        else:            
            if endpoint.startswith('/'):
                if base_url.endswith('/'):                    
                    endpoint = endpoint[1:]
            else:
                if not base_url.endswith('/') and endpoint:
                    endpoint = f'/{endpoint}'
            
            if self.force_trailing_slash and not endpoint.endswith('/'):
                endpoint = f'{endpoint}/'

            url = f'{base_url}{endpoint}'

        if params:
            url += "?" + urlencode(params)
        
        return url
    

    def get_request_headers(self, url: str) -> MutableMapping[str,str]:
        headers = {**self.default_headers}
        return headers


    def get_dict_or_str_response(self, response: HTTPResponse|HTTPError) -> dict|str:
        result = self._decode_response(response)
        if isinstance(result, Exception):
            return str(result)
        return result


    def get_dict_response(self, response: HTTPResponse|HTTPError) -> dict:
        result = self._decode_response(response)
        if isinstance(result, Exception):
            raise result from None        
        return result


    def _decode_response(self, response: HTTPResponse|HTTPError) -> dict|Exception:
        rawdata = response.read()
        try:
            strdata = rawdata.decode('utf-8')
        except UnicodeDecodeError:
            strdata = str(rawdata)
            return ApiClientError("Invalid UTF-8", strdata, message_maxlen=self.print_error_maxlen)
        
        try:
            result = json.loads(strdata, cls=self.json_decoder_cls)
        except json.JSONDecodeError:
            return ApiClientError("Not JSON", strdata, message_maxlen=self.print_error_maxlen)
        
        if not isinstance(result, dict):
            return ApiClientError("Not dict", strdata, message_maxlen=self.print_error_maxlen)
        
        return result
        

class ApiClientError(Exception):
    def __init__(self, error: str|Exception, data: dict|str|None = None, *, message_maxlen: int|None = 400):
        self.prefix: str
        self.code_nature: str|None = None
        self.code: int|None = None

        if isinstance(error, HTTPError):
            self.prefix = error.reason
            self.code = error.status
            self.code_nature = 'status'
        elif isinstance(error, URLError):
            self.prefix = str(error.reason) if not isinstance(error.reason, str) else error.reason
            self.code = error.errno
            self.code_nature = 'errno'
        elif isinstance(error, str):
            self.prefix = error
        else:
            self.prefix = f"[{type(error).__name__}] {error}"

        self.data = data
        self.message_maxlen = message_maxlen
        super().__init__(self._prepare_message())


    def _prepare_message(self):
        message = self.prefix

        if self.code:
            message = (message + ' ' if message else '') + f"[{self.code_nature or 'code'}: {self.code}]"
        
        if self.data:
            if isinstance(self.data, dict):
                for key, value in self.data.items():
                    message = (message + '\n' if message else '') + f"{key}: {value}"
            else:
                message = (message + '\n' if message else '') + str(self.data)

        self.full_message = message
    
        if self.message_maxlen is not None and len(self.full_message) > self.message_maxlen:
            return self.full_message[0:self.message_maxlen] + '…'
        else:
            return self.full_message
