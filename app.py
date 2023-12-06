from flask import Flask, render_template
from flask_pymongo import PyMongo
from script_protein2ipr import process_protein2ipr
import re
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/proteins"
mongo = PyMongo(app)

@app.route('/')
def hello():
    return render_template('index.html')


# Route pour insérer les données de protéines dans la base de données.
@app.route('/insert/proteins')
def insert_proteins():
    proteins_data = open("data.tsv", "r")
    # Insertion des données du fichier dans la base de données.
    for line in proteins_data:
        protein = line.split('\t')
        
        if mongo.db.proteins.find_one({'Entry': protein[0]}) is None:
            mongo.db.proteins.insert_one({
                'Entry': protein[0],
                'Entry_name': protein[1],
                'Protein_names': protein[2],
                'GO': protein[3],
                'InterPro': [],
                'EC_number': protein[5],
                'GO_ID': protein[6]
            })
            iprs = [element for element in protein[4].split(';') if element]
            mongo.db.proteins.update_one(
                {'Entry': protein[0]},
                {'$push': {'InterPro': {'$each': iprs}}}
            )

    return "Done"

# Route pour calculer les liens entre les protéines et les insérer dans la base de données s'ils sont convenables.
@app.route('/insert/links')
def insert_links():
    with open("data.tsv", "r") as file:
        proteins_data = file.readlines()

    # Comparaison des protéines entre elles
    for i, line in enumerate(proteins_data):
        current_protein = line.split('\t')
        current_domain =  [element for element in current_protein[4].split(';') if element] # Domaine d'une protéine = la liste de ses IPRs
        if len(current_domain) == 0:
            continue
        for j, line2 in enumerate(proteins_data, start=i+1):
            compared_protein_line = line2.split('\t')
            if (current_protein[0] == compared_protein_line[0]):
                continue

            compared_domain = [element for element in compared_protein_line[4].split(';') if element]
            if len(compared_domain) == 0:
                continue

            union_domain = list(compared_domain)
            # Calcul de l'union des deux domaines (U)
            for ipr in current_domain:
                if ipr not in union_domain:
                    union_domain.append(ipr)
            
            inter_domain = []
            # Calcul de l'intersection des deux domaines (I)   
            for ipr in current_domain:
                if ipr in compared_domain:
                    inter_domain.append(ipr)
            jaccard_coeff = len(inter_domain) / len(union_domain)
            if(jaccard_coeff < 0.8) :
                continue
            else: 
                # Insertion du lien dans la base de données
                if mongo.db.links.find_one({'Entry' : current_protein[0] }) == None: 
                    mongo.db.links.insert_one({'Entry': current_protein[0], 'Links' : []})
                
                # Insertion du lien entre current_protein et compared_protein dans le tableau Links dans la base de données 
                to_insert = {compared_protein_line[0] : jaccard_coeff}
                # insert only if Links doesn't contain to_insert
                if mongo.db.links.find_one({'Entry': current_protein[0], 'Links': {'$elemMatch': to_insert}}) is None:
                    mongo.db.links.update_one({'Entry': current_protein[0]}, {'$push': {'Links': to_insert}})
        
    return "Done"

@app.route('/insert/go')
def insert_go():
    with open("data/go.obo", "r") as file:
        go_data = file.read()

    terms = re.split(r'\[Term\]\s*', go_data)
    terms = [term.strip() for term in terms if term.strip()]
    for term in terms:
        term_dict = {}
        lines = term.split('\n')
        current_key = None

        for line in lines:
            if line:
                key, value = re.split(r':\s*', line, 1)
                key = key.lower()
                
                # Si la clé est déjà présente dans le dictionnaire, ajouter la valeur au tableau
                if key in term_dict:
                    if not isinstance(term_dict[key], list):
                        term_dict[key] = [term_dict[key]]
                    term_dict[key].append(value.strip())
                else:
                    term_dict[key] = value.strip()
        if (mongo.db.go.find_one({'id': term_dict['id']}) is None):
            mongo.db.go.insert_one(term_dict)
        
    return "Done"
if __name__ == '__main__':
    app.run(debug=True)