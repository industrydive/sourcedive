## private settings

SECRET_KEY = ''  # UPDATE with random string

ALLOWED_HOSTS = [
    # local
    'localhost',
    '127.0.0.1',
    # staging
    '35.232.16.182',
]
INTERNAL_IPS = ['127.0.0.1']

## for local and test servers
TEST_ENV = True
## for prod server
# TEST_ENV = False

## project info

PROJECT_NAME = 'SourceDive'

## database local
db_engine = 'django.db.backends.postgresql_psycopg2'
db_name = 'sourcedive'
db_user = 'sourcediveuser'
db_password = 'sourcediveuser'
db_host = 'db'
db_port = '5432'

## social auth
SOCIAL_AUTH_PASSWORDLESS = True
SOCIAL_AUTH_ALWAYS_ASSOCIATE = True

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''  # UPDATE see lastpass
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''  # UPDATE see lastpass

SOCIAL_AUTH_GOOGLE_WHITELISTED_DOMAINS = ['industrydive.com']
