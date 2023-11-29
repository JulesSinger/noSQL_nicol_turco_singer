from flask import Flask
from flask_pymongo import PyMongo
from script_protein2ipr import process_protein2ipr
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/proteins"
mongo = PyMongo(app)

@app.route('/')
def hello():
    dictionnaire = process_protein2ipr()
    for key in dictionnaire:
        # insert only if not already in database
        if mongo.db.proteins.find_one({'protein_id': key}) == None:
            mongo.db.proteins.insert_one({'protein_id': key, 'iprs': dictionnaire[key]})
    
    return '<h1>Hello, World!</h1>'

app.run(debug=True)