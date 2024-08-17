import os
URL = "postgresql://{}:{}@{}:{}/{}"
# USER = "postgres"
# PASSWORD = "p455w0rdD3v3l0p"
# HOSTNAME = "localhost"
# PORT = "5432"
# DATABASE = "postgres"
USER = os.getenv('PG_USERNAME')
PASSWORD = os.getenv('PG_PASSWORD')
HOSTNAME = os.getenv('PG_HOSTNAME')
PORT = os.getenv('PG_PORT')
DATABASE = os.getenv('PG_DATABASE')