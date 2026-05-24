import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # EXTERNAL DATABASE
    DB_BOT = './instance/bot_new.db'

    # LOCAL DATABASE
    DB_EXERCISES = './instance/database.db'
    DB_AUTH = './instance/auth.db'

    ITEMS_PER_PAGE = 10