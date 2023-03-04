import os
from datetime import timedelta


class Config:
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.environ.get('DB_USER')}:" \
                              f"{os.environ.get('DB_PASS')}@{os.environ.get('DB_HOST')}:" \
                              f"5432/{os.environ.get('DB_NAME')}"
    SQLALCHEMY_ECHO = True
    DEBUG = True

print(Config.SQLALCHEMY_DATABASE_URI )
