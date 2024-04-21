import os

URL = "postgresql://{}:{}@{}:{}/{}"
USER = "postgres"#os.getenv('PG_USERNAME')
PASSWORD = "p455w0rdD3v3l0p"#os.getenv('PG_PASSWORD')
HOSTNAME = "localhost"#os.getenv('PG_HOSTNAME')
PORT = "5432"#os.getenv('PG_PORT')
DATABASE = "postgres"#os.getenv('PG_DATABASE')