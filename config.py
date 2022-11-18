from decouple import config

class Config:
    SECRET_KEY = config('SECRET_KEY')
    

class ConfigDB(Config):
    MYSQL_HOST = config('MYSQL_HOST')
    MYSQL_USER = config('MYSQL_USER') 
    MYSQL_PASSWORD = config('MYSQL_PASSWORD')
    MYSQL_DB = config('MYSQL_DB') 

myConfig = {
    'configfromEnv': ConfigDB
}