from flask import Flask, render_template
from flask_pymongo import PyMongo
from script_protein2ipr import process_protein2ipr
from neo4j import GraphDatabase

import re
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/proteins"
mongo = PyMongo(app)


class Neo4jGraph:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def create_protein_nodes(self, proteins):
        with self._driver.session() as session:
            session.run("CREATE (:Protein {name: $name})", name=proteins)

    def create_associations(self, base_protein, protein_associations):
        base_protein = str(base_protein) if not isinstance(base_protein, str) else base_protein
        with self._driver.session() as session:
                for associated_protein_dict in protein_associations:
                    for entry, coefficient in associated_protein_dict.items():
                        print(entry, coefficient)
                        entry_str = str(entry) if not isinstance(entry, str) else entry

                        session.run(
                            """
                                MERGE (a:Protein {name: $protein})
                                MERGE (b:Protein {name: $associated_protein})
                                CREATE (a)-[r:ASSOCIATED_WITH {coefficient: $coefficient}]->(b)
                            """,
                            protein=base_protein,
                            associated_protein=entry_str,
                            coefficient=coefficient
                        )

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
                'EC_number': protein[6],
                'GO_ID': []
            })
            iprs = [element for element in protein[4].split(';') if element]
            mongo.db.proteins.update_one(
                {'Entry': protein[0]},
                {'$push': {'InterPro': {'$each': iprs}}}
            )

            go_ids_str = protein[4]
            go_ids_list = [go_id.strip() for go_id in go_ids_str.split(';')]
            mongo.db.proteins.update_one(
                {'Entry': protein[0]},
                {'$push': {'GO_ID': {'$each': go_ids_list}}}
            )

    return "Done"

# Route pour calculer les liens entre les protéines et les insérer dans la base de données s'ils sont convenables.
@app.route('/insert/links')
def insert_links():
    print("Insertion des liens entre les protéines")
    with open("data.tsv", "r") as file:
        proteins_data = file.readlines()

    # Comparaison des protéines entre elles
    for i, line in enumerate(proteins_data):
        current_protein = line.split('\t')
        current_domain =  [element for element in current_protein[4].split(';') if element] # Domaine d'une protéine = la liste de ses IPRs
        if len(current_domain) == 0:
            continue
        for j, ligne2 in enumerate(proteins_data[i+1:]):
            compared_protein_line = ligne2.split('\t')
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
            if(jaccard_coeff < 0.90) :
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

# correct the GO_ID field un proteins collection to transform it in an Array
@app.route("/correctdb")
def correct_db(): 
    # transform GO_ID : "GO:0000045; GO:0000422; GO:0001666; GO:0005776"
    # into GO_ID : ["GO:0000045", "GO:0000422", "GO:0001666", "GO:0005776"]
    proteins = mongo.db.proteins.find()
    # Mise à jour de chaque document
    for protein in proteins:
        # Vérification de la présence de la clé GO_ID
        if 'GO_ID' in protein:
            # Transformation de la chaîne de caractères en tableau
            go_ids_str = protein['GO_ID']
            go_ids_list = [go_id.strip() for go_id in go_ids_str.split(';')]
            # Mise à jour du document dans la collection
            mongo.db.proteins.update_one(
                {'_id': protein['_id']},
                {'$set': {'GO_ID': go_ids_list}}
            )

    return 'DONE'

@app.route('/insert/graph')
def insert_graph():
 # Initialisation de neo4j
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "password"
    neo4j_graph = Neo4jGraph(uri, user, password)
 # Création des noeuds neo4j
    listProt = mongo.db.links.find({})
    proteinDataList = []
    for protein in listProt:
        proteinData = mongo.db.links.find_one({'_id' : protein['_id'] })
        proteinDataList.append(proteinData)
        neo4j_graph.create_protein_nodes(proteinData['Entry'])

    for proteinData in proteinDataList:
        
        if proteinData['Links'] == None or proteinData['Links'] == []:
            continue
        neo4j_graph.create_associations(protein, proteinData['Links'])
    
    neo4j_graph.close()


if __name__ == '__main__':
    app.run(debug=True)