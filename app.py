from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/proteins"
mongo = PyMongo(app)

@app.route('/')
def hello():
    mongo.db.inventory.insert_one({'name': 'test'})
    mongo.db.proteins.insert_one({'name': 'test'})
    return '<h1>Hello, World!</h1>'

app.run(debug=True)