import os

APP = os.getenv('APP', 'app')
ENV = os.getenv('ENV', 'local')
DEBUG = os.getenv('DEBUG', '')
TEST = os.getenv('TEST', '')
APP_IMAGE_VERSION = os.getenv('PHANTOM_MASK_API_VERSION') or '?'
APP_URL_VERSION = (1, 0)


IS_LOCAL_ENV: bool = (ENV == 'local')
IS_DEBUG: bool = True if DEBUG else False
IS_TEST: bool = True if TEST else False

SENTRY_DSN = os.getenv('SENTRY_DSN', None)
NEW_RELIC_APP_NAME = os.getenv('NEW_RELIC_APP_NAME', None)
NEW_RELIC_LICENSE_KEY = os.getenv('NEW_RELIC_LICENSE_KEY', None)
OPENAPI_EXAMPLE_DIR = os.getenv(
    'OPENAPI_EXAMPLE_DIR',
    os.path.join(os.path.dirname(__file__), 'openapi_example'),
)

TIMEOUT_SECHOND: int = int(os.getenv('TIMEOUT_SECHOND') or '60')
