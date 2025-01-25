from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_random_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.mailersend.net'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MS_X7t7yf@trial-pr9084zqo2m4w63d.mlsender.net')
    MAIL_PASSWORD = os.environ.get('mssp.05Qzohc.jy7zpl99kepl5vx6.sEgZMEq')
    TWILIO_ACCOUNT_SID = os.environ.get('ACa0049db41abd3f693e3727051117c7cd')
    TWILIO_AUTH_TOKEN = os.environ.get('e1584b10fb08a572b21d38127eb3df75')
