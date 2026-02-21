import os
from dotenv import load_dotenv

load_dotenv()

MAX_URL_LENGTH = 2048
SHORT_LINK_MAX_LEN = 16
SHORT_LINK_PATTERN = r'^[a-zA-Z0-9]+$'

DISK_TOKEN = os.environ.get('DISK_TOKEN')
YANDEX_API_BASE_URL = 'https://cloud-api.yandex.net/v1/disk/resources'
YANDEX_HEADERS = {'Authorization': f'OAuth {DISK_TOKEN}'}

REDIRECT_ENDPOINT = 'redirect_view'
