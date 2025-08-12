import os
from dataclasses import dataclass, field
import requests
from dotenv import load_dotenv

# Suppress the warnings from urllib3
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

load_dotenv()


@dataclass
class HTTPSettings:
    """Singleton class to store global http settings for this session."""
    api_body: dict = field(default_factory=dict)
    be_url: str = "https://api.lattica.ai"
    api_url: str = be_url + "/api/do_action"


_http_settings = HTTPSettings()

if os.getenv('LATTICA_BE_URL'):
    _http_settings.be_url = os.getenv('LATTICA_BE_URL')
    _http_settings.api_url = _http_settings.be_url + "/api/do_action"


def set_api_body(api_body: dict) -> None:
    _http_settings.api_body = api_body


def get_api_body() -> dict:
    return _http_settings.api_body


def set_be_url(be_url: str) -> None:
    _http_settings.be_url = be_url


def get_be_url() -> str:
    return _http_settings.be_url


def set_api_url(api_url: str) -> None:
    _http_settings.api_url = api_url


def get_api_url() -> str:
    return _http_settings.api_url
