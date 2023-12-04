def process_protein2ipr():
    # Création du dictionnaire
    dictionnaire = {}
    # read protein2ipr file
    f = open("protein2ipr_extrait.txt", "r")
    for line in f:
        elements = line.split('\t')
        identifiant = elements[0]
        ipr = elements[1]
        if identifiant not in dictionnaire:
            dictionnaire[identifiant] = []
        dictionnaire[identifiant].append(ipr)
    
    # Fermeture du fichier
    f.close()

    return dictionnaire 