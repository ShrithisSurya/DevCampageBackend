import os

class Config:
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/newsletter')
    SECRET_KEY='bd13c8d00deb88e1852161cdd4f2363a'