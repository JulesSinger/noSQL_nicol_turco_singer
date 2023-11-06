from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('localhost', 27017)

db = client.flask_db

@app.route('/')
def hello():
    return '<h1>Hello, World!</h1>'