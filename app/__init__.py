from flask import Flask
from config import settings

app = Flask(__name__)
app.secret_key = settings.SECRET_KEY

from app import routes