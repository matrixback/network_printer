# coding: utf-8
import logging

SECRET_KEY = 'MATRIX'
SQLALCHEMY_DATABASE_URI = 'sqlite:////files.db'
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
PASSWORD = 'hack'

logging.basicConfig(
    level=logging.INFO,
    filename="log",
    filemode='a',
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)