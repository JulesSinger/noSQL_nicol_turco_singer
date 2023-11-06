créer un environnement virtuel python :
python3 -m venv env

activer l'environnement local : 
source env/bin/activate

télécharger les dépendances : 
pip install -r requirements.txt

(nouvelle dépendance ? -> "pip freeze > requirements.txt" dans le terminal)

pour lancer l'application : 

dans le terminal : 
export FLASK_APP=app
export FLASK_ENV=development
flask run