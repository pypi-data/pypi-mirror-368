import os
from urllib.parse import urlparse
from enum import Enum
import shutil
from lattica_common import http_settings

class RunMode(Enum):
    RUN_LOCAL_WITH_API = 1
    RUN_CLOUD = 2


# Read from environment variable, default to CLOUD for production
_run_mode_str = os.getenv('LATTICA_RUN_MODE', 'CLOUD')
RUN_MODE = RunMode.RUN_LOCAL_WITH_API if _run_mode_str == 'LOCAL' else RunMode.RUN_CLOUD

_DEV_BACKEND_URL = "http://localhost:3050"
_DEV_API_URL = f'{_DEV_BACKEND_URL}/api/do_action'

if RUN_MODE == RunMode.RUN_LOCAL_WITH_API:
    http_settings.set_be_url(_DEV_BACKEND_URL)
    http_settings.set_api_url(_DEV_API_URL)


# path to local folder replacing cloud storage shared with the worker
def _find_storage_base() -> str:
    script_path = os.path.dirname(os.path.realpath(__file__))
    while not script_path.endswith('/client'):
        script_path = os.path.dirname(script_path)
    return f"{os.path.dirname(script_path)}/tmp_storage"


_DEV_STORAGE_BASE = _find_storage_base()


def _mock_upload_file(folder: str, file_path: str, s3_key: str) -> None:
    dest_file_name = _extract_file_name_from_s3_key(s3_key)
    # create localhost storage folder if needed
    file_location = os.path.join(_DEV_STORAGE_BASE, folder)
    if not os.path.exists(file_location):
        print(f"creating tmp storage {file_location}")
        os.makedirs(file_location)
    shutil.copyfile(file_path, os.path.join(file_location, dest_file_name))


def mock_upload_model(file_path: str, s3_key: str) -> None:
    _mock_upload_file("models", file_path, s3_key)


def mock_upload_pk(file_path: str, s3_key: str) -> None:
    _mock_upload_file("pks", file_path, s3_key)


def _extract_file_name_from_s3_key(s3_key: str) -> str:
    return s3_key.rstrip('/').split('/')[-1]
