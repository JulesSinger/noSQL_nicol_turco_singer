## Proteine2IPR
Liste tous les IPR d'une protéine

1   ID protein
2   InterPro
3   Protein Names?
4   ...

## GOA 
Pour chaque GO on associe une protéine et un interpro

1       DB
2       DB_Object_ID
3       DB_Object_Symbol
4       Qualifier
5       GO_ID
6       DB:Reference
7       Evidence Code
8       With (or) From
9       Aspect
10      DB_Object_Name
11      DB_Object_Synonym
12      DB_Object_Type
13      Taxon and Interacting taxon
14      Date
15      Assigned_By
16      Annotation_Extension
17      Gene_Product_Form_ID

## GO Basic
Décrit ce que fait chaque GO

### Exemple:
> id: GO:0000001
> name: mitochondrion inheritance
> namespace: biological_process
> def: "The distribution of mitochondria, including the mitochondrial genome, into daughter cells after mitosis or meiosis, mediated by interactions between mitochondria and the cytoskeleton." [GOC:mcc, PMID:10873824, PMID:11389764]
> synonym: "mitochondrial inheritance" EXACT []
> is_a: GO:0048308 ! organelle inheritance
> is_a: GO:0048311 ! mitochondrion distribution

## Enzyme.dat
- ID  Identification                         (Begins each entry; 1 per entry)
- DE  Description (official name)            (>=1 per entry)
- AN  Alternate name(s)                      (>=0 per entry)
- CA  Catalytic activity                     (>=1 per entry)
- CC  Comments                               (>=0 per entry)
- PR  Cross-references to PROSITE            (>=0 per entry)
- DR  Cross-references to Swiss-Prot         (>=0 per entry)


GO Basic <-> GOA : GO

## Liaison des données
### ProteinID
GOA -> 2e colonne (Object ID )
Protein2IPR -> 1ere colonne 

## TODO
Faire 2 script Python:
- 1 pour interpro HashMap<ID, ArrayList<IPR>> -> Jules/Bastien
- 1 pour GOA HashMap<ID, ArrayList<GO>> -> Benoit
Pour chaque protéine:
Récupérer la liste des IPR et la liste des GO number.

    