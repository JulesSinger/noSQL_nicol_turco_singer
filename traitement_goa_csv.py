import csv

def generer_listes(fichier_csv):
    # Créer des dictionnaires pour stocker les listes des colonnes GO et Interpro ainsi que les numéros de ligne pour chaque identifiant
    listes_GO_par_identifiant = {}
    listes_Interpro_par_identifiant = {}

    with open(fichier_csv, 'r', newline='', encoding='utf-8') as csv_file:
        # Spécifier le délimiteur comme une virgule
        csv_reader = csv.reader(csv_file, delimiter=',')

        for num_ligne, row in enumerate(csv_reader, start=1):
            # Ignorer les lignes vides
            if not row:
                continue

            # Assurez-vous que row a suffisamment d'éléments avant d'accéder à row[2]
            if len(row) >= 3:
                # Récupérer l'identifiant (colonne 1), la valeur colonne 3 et la valeur colonne 4
                identifiant = row[1]
                valeur_GO = row[4]
                valeur_Interpro = row[7]

                

                # Ajouter la valeur de la colonne 3 à la liste correspondante dans le dictionnaire
                if identifiant in listes_GO_par_identifiant:
                    listes_GO_par_identifiant[identifiant].append(valeur_GO)
                else:
                    listes_GO_par_identifiant[identifiant] = [valeur_GO]

                # Ajouter la valeur de la colonne 4 à la liste correspondante dans le dictionnaire
                if identifiant in listes_Interpro_par_identifiant:
                    if '|' in valeur_Interpro:
                        # Diviser la chaîne en fonction du délimiteur '|'
                        parties = valeur_Interpro.split('|')
                
                        # Filtrer les parties qui commencent par 'InterPro:'
                        for part in parties:
                            if part.startswith('InterPro:'):
                                listes_Interpro_par_identifiant[identifiant].append(part)
                        #interpro_parts = [part.strip() for part in parties if part.startswith('InterPro:')]
                    else:
                        # Si la chaîne ne contient pas '|', vérifier si elle commence par 'InterPro:'
                        if valeur_Interpro.startswith('InterPro:'):
                            listes_Interpro_par_identifiant[identifiant].append(valeur_Interpro)
                else:
                    listes_Interpro_par_identifiant[identifiant] = []
                    if '|' in valeur_Interpro:
                        # Diviser la chaîne en fonction du délimiteur '|'
                        parties = valeur_Interpro.split('|')
                
                        # Filtrer les parties qui commencent par 'InterPro:'
                        for part in parties:
                            if part.startswith('InterPro:'):
                                listes_Interpro_par_identifiant[identifiant].append(part)
                        #interpro_parts = [part.strip() for part in parties if part.startswith('InterPro:')]
                    else:
                        # Si la chaîne ne contient pas '|', vérifier si elle commence par 'InterPro:'
                        if valeur_Interpro.startswith('InterPro:'):
                            listes_Interpro_par_identifiant[identifiant].append(valeur_Interpro)
            # else:
            #     print(f"Attention: La ligne {num_ligne} n'a pas assez d'éléments.")

    # Retourner les dictionnaires de listes
    return listes_GO_par_identifiant, listes_Interpro_par_identifiant

# Remplacez "votre_fichier.csv" par le nom réel de votre fichier CSV
fichier_csv = "goa.csv"
liste_GO_par_identifiant, liste_Interpro_par_identifiant = generer_listes(fichier_csv)