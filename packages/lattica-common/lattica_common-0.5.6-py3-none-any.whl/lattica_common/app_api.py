import os

from lattica_common.version_utils import get_module_info
import json, requests
import secrets
import string
import typing
from typing import TypeAlias, Optional, Union, Dict

from lattica_common import http_settings

AppResponse: TypeAlias = Union[str, dict]
WorkerStatus: TypeAlias = Dict[str, str]
ModelId: TypeAlias = str


def generate_random_token_name(n: int) -> str:
    return ''.join(secrets.choice(string.ascii_letters + string.digits + '-_') for _ in range(n))


class HttpClient:
    def __init__(self, session_token: str = None, module_name: str = None):
        self.session_token = session_token
        self.module_name = module_name
        # Use the provided module name or try to detect it
        self.module_version = get_module_info(module_name)

    def send_http_request(self, req_name: str, req_params: Optional[dict] = None) -> AppResponse:
        req_params = req_params if req_params else {}
        
        # Add client module and version information
        client_info = {
            "client_info": {
                "module": self.module_name,
                "version": self.module_version
            }
        }
        # Merge client info with request params
        full_params = {**req_params, **client_info}

        headers = {
            'Content-Type': 'application/json',
        }

        if self.session_token:
            headers['Authorization'] = f'Bearer {self.session_token}'
        
        response = requests.post(
            f'{http_settings.get_be_url()}/{req_name}',
            headers=headers,
            json=full_params
        )
        if response.ok:
            response_json = json.loads(response.text)
            
            # Check for version incompatibility error
            if 'error' in response_json and response_json.get('error_code') == 'CLIENT_VERSION_INCOMPATIBLE':
                raise ClientVersionError(response_json['error'], response_json.get('min_version'))
                
            if 'error' not in response_json:
                return response_json["result"]

        raise Exception(f'FAILED {req_name} with error: {response.text}')

    def send_http_file_request(
            self,
            req_name: str,
            req_params: Optional[dict] = None,
            model_file_path: str = None
    ) -> dict:
        if model_file_path is None:
            raise ValueError("model_file_path must be provided")

        req_params = req_params if req_params else {}
        
        # Add client module and version information
        client_info = {
            "client_module": self.module_name,
            "client_version": self.module_version
        }
        # Merge client info with request params
        full_params = {**req_params, **client_info}
        
        url = f'{http_settings.get_be_url()}/{req_name}'

        headers = {
            'Authorization': f'Bearer {self.session_token}'
        }

        with open(model_file_path, 'rb') as file_obj:
            files = {
                'plain_model_file': file_obj
            }
            response = requests.post(url, headers=headers, data=full_params, files=files)

        if response.ok:
            try:
                response_json = response.json()
                
                # Check for version incompatibility error
                if 'error' in response_json and response_json.get('error_code') == 'CLIENT_VERSION_INCOMPATIBLE':
                    raise ClientVersionError(response_json['error'], response_json.get('min_version'))
                    
                if 'error' not in response_json:
                    return response_json.get("result", response_json)
                else:
                    raise Exception(f"Server returned error: {response_json['error']}")
            except json.JSONDecodeError:
                raise Exception("Invalid JSON response")
        else:
            raise Exception(f'FAILED {req_name} with error: {response.text}')

class LatticaAppAPI:
    def __init__(self, account_token: str, module_name: str = None):
        self.http_client = HttpClient(account_token, module_name=module_name)

    # ============== start API calls ============== #

    @staticmethod
    def upload_file(file_path: str, upload_url: str) -> None:
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            # To avoid: header (Transfer-Encoding: chunked) that S3 does not support for pre-signed PUT uploads.
            res = requests.put(upload_url, data=b'')
        else:
            with open(file_path, "rb") as file:
                res = requests.put(upload_url, data=file)
        res.raise_for_status()

    def alert_upload_complete(self, key: str, params_config=None) -> str:
        if params_config is None:
            response = self.http_client.send_http_request(
                'api/files/upload_complete',
                req_params={'s3Key': key}
            )
        else:
            params_config_copy = params_config.copy()
            is_ckks = params_config_copy.pop('is_ckks')
            init_context_params = {
                'params_config': params_config_copy,
                'is_ckks': is_ckks
            }
            response = self.http_client.send_http_request(
                'api/files/upload_complete',
                req_params={'s3Key': key, 'initContextParams': init_context_params}
            )
        return response

    def upload_user_file(self, file_path: str) -> str:
        response = self.http_client.send_http_request('api/token/get_pk_upload_url')
        upload_url = typing.cast(str, response['s3Url'])
        self.upload_file(file_path, upload_url)
        return response['s3Key']




# Custom exception for version incompatibility
class ClientVersionError(Exception):
    """Raised when the client version is incompatible with the server."""
    
    def __init__(self, message, min_version=None):
        self.message = message
        self.min_version = min_version
        super().__init__(self.get_user_message())
    
    def get_user_message(self):
        base_msg = "Your client is outdated and incompatible with the server."
        if self.min_version:
            return f"{base_msg} Please upgrade to version {self.min_version} or higher."
        return f"{base_msg} Please upgrade to the latest version."

