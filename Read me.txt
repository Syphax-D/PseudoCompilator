Membres du groupe :
- DIB Syphax
- AMROUN Said

Ce fichier 'comp.py' est l'implémentation complète d'un compilateur et interpréteur pour un mini-langage de programmation inspiré du Pascal (que nous pourrions appeler "Mini-Pascal"). 

Le fichier contient toutes les phases classiques de la compilation regroupées dans un seul script :
1. Analyse Lexicale : Lit le code source caractère par caractère, ignore les commentaires/espaces et les regroupe en mots ou "tokens" (mots-clés, identifiants, symboles).
2. Analyse Syntaxique : Vérifie que l'enchaînement des tokens respecte les règles de grammaire du langage (par exemple, un 'SI' doit être suivi de 'ALORS'). C'est un parser récursif descendant.
3. Analyse Sémantique : Vérifie le sens du code (par exemple, s'assurer qu'une variable a bien été déclarée dans la section 'VAR' avant d'être utilisée, ou qu'on n'affecte pas une chaîne à un entier).
4. Génération de Code : Convertit la syntaxe vérifiée en un code "machine" intermédiaire, appelé P-Code (comme l'assembleur), destiné à une machine virtuelle à pile.
5. Machine Virtuelle : Exécute le P-Code généré ligne par ligne pour faire tourner le programme.

Voici l'explication détaillée de chaque classe présente dans le code :

 1. T_UNILEX(Enum)
Cette classe est une énumération qui définit tous les types de "tokens" (unités lexicales) que l'analyseur lexical peut reconnaître dans le programme source.
- Exemples : 'motcle' (pour SI, FIN, DEBUT), 'ident' (nom de variable), 'ent' (nombre entier), 'ch' (chaîne de caractères), ou encore les symboles opérateurs/ponctuation comme 'virg' (virgule), 'plus' (+), 'aff' (:= pour l'affectation).

 2. TYPE_ERREUR(Enum)
Une simple énumération pour catégoriser les erreurs rencontrées lors de la compilation afin d'afficher des messages d'erreur pertinents :
- LEXICAL : Erreur de frappe, caractère non reconnu ou chaîne mal fermée.
- SYNTAXIQUE : Mot manquant ou structure incorrecte (ex: 'ALORS' manquant après un 'SI').
- SEMANTIQUE : Problème de type ou variable non déclarée.

 3. EntreeIdent
Une toute petite classe (une structure de données) qui représente une entrée dans la table des identificateurs du lexique.
- Elle stocke simplement le 'nom' de l'identificateur (ex: un nom de variable comme 'MaVariable').

 4. TableIdentificateurs
Cette classe gère la liste de tous les identificateurs uniques (noms de variables, constantes) rencontrés dans le code source lors de l'analyse lexicale. 
- Méthodes clés : Elle maintient la liste triée par ordre alphabétique. La méthode '_recherche_dichotomique' (recherche binaire) permet de savoir très rapidement de manière optimisée si un identificateur existe déjà, et 'ajouter' l'insère au bon endroit si ce n'est pas le cas.

 5. Symbole (définie avec @dataclass)
Lors de la phase de déclaration ('VAR' ou 'CONST'), chaque identificateur devient un Symbole qui possède des attributs sémantiques.
- nom : Le nom de la variable ou constante.
- genre : "var" (variable) ou "const" (constante).
- typc : Type de donnée (0 pour ENTIER, 1 pour CHAINE).
- adr : L'adresse mémoire allouée à cette variable dans la machine virtuelle (pour savoir où la stocker/lire).
- val : Si c'est une constante mathématique, sa valeur est stockée ici directement.

 6. TableSymboles
C'est le "dictionnaire" (table de hachage) du compilateur qui stocke et gère les instances de la classe Symbole.
- Elle est utilisée pendant l'analyse syntaxique/sémantique. À chaque fois qu'on déclare une variable, elle s'ajoute ici ('ajouter'). Lorsqu'on utilise une variable dans un calcul, le compilateur appelle la méthode 'get' ou 'existe' pour vérifier que la variable a bien été déclarée au préalable et a le bon type.

 7. OP
Ce n'est pas vraiment une classe avec des éléments d'instance, mais plutôt un conteneur pseudo-enum pour les Opcodes (Codes d'opération) du P-Code. Il s'agit du vocabulaire d'instructions de la machine virtuelle :
- Mathématiques : 'ADDI' (+), 'SOUS' (-), 'MULT' (*), 'DIVI' (/), 'MOIN' (inversion de signe).
- Mémoire & variables : 'EMPI' (Empiler une valeur), 'CONT' (Charger la valeur d'une variable), 'AFFE' (Affecter une valeur à une variable).
- Entrées/Sorties : 'LIRE' (Input utilisateur), 'ECRE' / 'ECRC' / 'ECRL' (Afficher à l'écran).
- Sauts (Conditions et Boucles) : 'ALLE' (Aller à : saut inconditionnel), 'ALSN' (Aller Si Nul : saut conditionnel, utilisé pour sortir des boucles TANTQUE ou ignorer les branches SI).
- STOP : Terminer le programme.

 Comment tout s'articule  (Résumé du flux)
1. Le script commence en bas ('if __name__ == "__main__":'), charge 'Code.minipascal' et appelle 'INITIALISER()'.
2. La fonction 'compiler_et_executer()' démarre la compilation. La fonction magique 'PROG()' (le parser) est appelée.
3. Le parser demande des tokens au scanner ('ANALEX()'). Selon le token recu, il appelle 'DECL_VAR()', 'BLOC()', 'INST_COND()' etc. (Descente récursive).
4. Lorsque le parser vérifie qu'une instruction est correcte (ex: 'A := 5'), il génère le bytecode via 'emit()' (ex: 'EMPI 5', 'AFFE adr_A'). Ces opérations atterrissent dans la liste globale 'P_CODE'.
5. Enfin, la fonction 'interpreter()' (la machine virtuelle) boucle sur ce tableau 'P_CODE'. Elle manipule la pile d'exécution virtuelle ('PILEX') et la mémoire ('MEMVAR') pour exécuter concrètement le programme compilé que vous avez écrit
