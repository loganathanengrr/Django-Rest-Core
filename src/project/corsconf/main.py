CORS_ORIGIN_ALLOW_ALL  = True


CORS_ORIGIN_REGEX_WHITELIST = ()


CORS_URLS_REGEX = r'^/api/.*$' # CORS HEADERS ENBALED


CORS_ORIGIN_WHITELIST = (
)

from corsheaders.defaults import default_headers


CORS_ALLOW_HEADERS = default_headers + (
    'X-CSRFToken',
    'Cache-Control',
)