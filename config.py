import os 

class Config:
    SECRE_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-know'
    