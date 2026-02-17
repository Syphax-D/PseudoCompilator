#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from enum import Enum

# 1. TYPES

class T_UNILEX(Enum):
    """Énumération des unités lexicales du langage mini-Pascal"""
    motcle = 1
    ident = 2
    ent = 3
    ch = 4
    virg = 5
    ptvirg = 6
    point = 7
    deuxpts = 8
    parouv = 9
    parfer = 10
    inf = 11
    sup = 12
    eg = 13
    plus = 14
    moins = 15
    mult = 16
    divi = 17
    infe = 18
    supe = 19
    diff = 20
    aff = 21

class TYPE_ERREUR(Enum):
    
    LEXICAL = "LEXICALE"
    SYNTAXIQUE = "SYNTAXIQUE"
    SEMANTIQUE = "SEMANTIQUE"


# 2. CONSTANTES

LONG_MAX_IDENT = 20      # Longueur maximale d'un identificateur
LONG_MAX_CHAINE = 50     # Longueur maximale d'une chaîne de caractères
NB_MOTS_RESERVES = 7     # Nombre de mots-clés réservés
MAXINT = 32767           # Valeur maximale pour un entier (16 bits)


# 3. STRUCTURE DE LA TABLE DES IDENTIFICATEURS

class EntreeIdent:
    def __init__(self, nom: str):
        self.nom = nom
    
    def __repr__(self):
        return self.nom


class TableIdentificateurs:
    def __init__(self):
        self.entrees = []  # Liste triée de pointeurs vers EntreeIdent
    
    def _recherche_dichotomique(self, nom: str):
        """
        Recherche dichotomique interne.
        Retourne: (trouve, position)
          - trouve: True si l'identificateur existe
          - position: index où insérer si non trouvé
        """
        gauche = 0
        droite = len(self.entrees) - 1
        
        while gauche <= droite:
            milieu = (gauche + droite) // 2
            nom_milieu = self.entrees[milieu].nom
            
            if nom_milieu == nom:
                return (True, milieu)
            elif nom_milieu < nom:
                gauche = milieu + 1
            else:
                droite = milieu - 1
        
        return (False, gauche)  # Non trouvé, position d'insertion = gauche
    
    def rechercher(self, nom: str) -> bool:
        """Vérifie si un identificateur existe dans la table."""
        trouve, _ = self._recherche_dichotomique(nom)
        return trouve
    
    def ajouter(self, nom: str):
        existe, pos = self._recherche_dichotomique(nom)
        if not existe:
            self.entrees.insert(pos, EntreeIdent(nom))
    
    def afficher(self):
        """Affiche le contenu trié de la table des identificateurs."""
        print("\n" + "=" * 70)
        print(f"TABLE DES IDENTIFICATEURS ({len(self.entrees)} identificateurs)")
        print("=" * 70)
        if len(self.entrees) == 0:
            print("  (aucun identificateur trouvé dans le programme source)")
        else:
            print("Identificateurs (triés alphabétiquement) :")
            print("-" * 70)
            for i, entree in enumerate(self.entrees, 1):
                print(f"  {i:3}. {entree.nom}")
        print("=" * 70 + "\n")


# 4. VARIABLES GLOBALES

# Fichier texte contenant le programme source
SOURCE = None

# Dernier caractère lu dans le fichier source
CARLU = ''

# Dernier nombre entier lu
NOMBRE = 0

# Dernier identificateur/mot-clé/chaîne lu
CHAINE = ''

# Numéro de la ligne courante dans le fichier source
NUM_LIGNE = 1

# Tableau des mots-clés réservés
TABLE_MOTS_RESERVES = [
    'CONST',
    'DEBUT',
    'ECRIRE',
    'FIN',
    'LIRE',
    'PROGRAMME',
    'VAR'
]

TABLE_IDENT = TableIdentificateurs()


# 5. FONCTIONS DE L'ANALYSEUR LEXICAL

def ERREUR(type_erreur: TYPE_ERREUR, message: str):
    """Affiche un message d'erreur typé avec le numéro de ligne."""
    global NUM_LIGNE
    print(f"\nERREUR {type_erreur.value} LIGNE {NUM_LIGNE}: {message}", file=sys.stderr)
    sys.exit(1)


def LIRE_CAR():
    global SOURCE, CARLU, NUM_LIGNE
    CARLU = SOURCE.read(1)
    if CARLU == '\n':
        NUM_LIGNE += 1


def SAUTER_SEPARATEURS():
    global CARLU
    while True:
        while CARLU in [' ', '\t', '\n', '\r']:
            LIRE_CAR()
        if CARLU == '{':
            nb_imbrication = 1
            LIRE_CAR()
            while nb_imbrication > 0:
                if not CARLU:
                    ERREUR(TYPE_ERREUR.LEXICAL, "commentaire non fermé")
                elif CARLU == '{':
                    nb_imbrication += 1
                    LIRE_CAR()
                elif CARLU == '}':
                    nb_imbrication -= 1
                    if nb_imbrication > 0:
                        LIRE_CAR()
                else:
                    LIRE_CAR()
            LIRE_CAR()
        else:
            break


def RECO_ENTIER():
    global CARLU, NOMBRE
    valeur = 0
    while '0' <= CARLU <= '9':
        chiffre = ord(CARLU) - ord('0')
        if valeur > MAXINT // 10:
            ERREUR(TYPE_ERREUR.LEXICAL, "entier trop grand (max 32767)")
        valeur = valeur * 10
        if valeur > MAXINT - chiffre:
            ERREUR(TYPE_ERREUR.LEXICAL, "entier trop grand (max 32767)")
        valeur += chiffre
        LIRE_CAR()
    NOMBRE = valeur


def RECO_CHAINE():
    global CARLU, CHAINE
    CHAINE = ''
    if CARLU != "'":
        ERREUR(TYPE_ERREUR.LEXICAL, "caractère illégal")
    LIRE_CAR()
    while True:
        if CARLU == "'":
            LIRE_CAR()
            if CARLU == "'":
                CHAINE += "'"
                if len(CHAINE) > LONG_MAX_CHAINE:
                    ERREUR(TYPE_ERREUR.LEXICAL, "chaîne trop longue (max 50 caractères)")
                LIRE_CAR()
            else:
                break
        elif CARLU == '\n' or CARLU == '':
            ERREUR(TYPE_ERREUR.LEXICAL, "apostrophe non fermée")
        else:
            CHAINE += CARLU
            if len(CHAINE) > LONG_MAX_CHAINE:
                ERREUR(TYPE_ERREUR.LEXICAL, "chaîne trop longue (max 50 caractères)")
            LIRE_CAR()
    return T_UNILEX.ch


def RECO_IDENT_OU_MOT_RESERVE():
    
    global CARLU, CHAINE, TABLE_IDENT
    
    CHAINE = ''
    longueur = 0
    
    # Lecture de l'identificateur/mot-clé
    while ('A' <= CARLU <= 'Z') or ('a' <= CARLU <= 'z') or ('0' <= CARLU <= '9') or CARLU == '_':
        if 'a' <= CARLU <= 'z':
            car_maj = chr(ord(CARLU) - 32)
        else:
            car_maj = CARLU
        if longueur < LONG_MAX_IDENT:
            CHAINE += car_maj
            longueur += 1
        LIRE_CAR()
    
    # Recherche dichotomique dans les mots réservés
    def EST_UN_MOT_RESERVE():
        gauche = 0
        droite = NB_MOTS_RESERVES - 1
        while gauche <= droite:
            milieu = (gauche + droite) // 2
            if TABLE_MOTS_RESERVES[milieu] == CHAINE:
                return True
            elif TABLE_MOTS_RESERVES[milieu] < CHAINE:
                gauche = milieu + 1
            else:
                droite = milieu - 1
        return False
    
    if EST_UN_MOT_RESERVE():
        return T_UNILEX.motcle
    else:
        if not TABLE_IDENT.rechercher(CHAINE):
            TABLE_IDENT.ajouter(CHAINE)
        return T_UNILEX.ident


def RECO_SYMB():
    global CARLU
    c = CARLU
    LIRE_CAR()
    if c == ',':
        return T_UNILEX.virg
    elif c == ';':
        return T_UNILEX.ptvirg
    elif c == '.':
        if CARLU == '':
            return T_UNILEX.point
        else:
            ERREUR(TYPE_ERREUR.LEXICAL, "caractère illégal")
    elif c == ':':
        if CARLU == '=':
            LIRE_CAR()
            return T_UNILEX.aff
        else:
            return T_UNILEX.deuxpts
    elif c == '(':
        return T_UNILEX.parouv
    elif c == ')':
        return T_UNILEX.parfer
    elif c == '<':
        if CARLU == '=':
            LIRE_CAR()
            return T_UNILEX.infe
        elif CARLU == '>':
            LIRE_CAR()
            return T_UNILEX.diff
        else:
            return T_UNILEX.inf
    elif c == '>':
        if CARLU == '=':
            LIRE_CAR()
            return T_UNILEX.supe
        else:
            return T_UNILEX.sup
    elif c == '=':
        return T_UNILEX.eg
    elif c == '+':
        return T_UNILEX.plus
    elif c == '-':
        return T_UNILEX.moins
    elif c == '*':
        return T_UNILEX.mult
    elif c == '/':
        return T_UNILEX.divi
    else:
        ERREUR(TYPE_ERREUR.LEXICAL, "caractère illégal")


def ANALEX():
    global CARLU
    SAUTER_SEPARATEURS()
    if '0' <= CARLU <= '9':
        RECO_ENTIER()
        return T_UNILEX.ent
    elif CARLU == "'":
        return RECO_CHAINE()
    elif ('A' <= CARLU <= 'Z') or ('a' <= CARLU <= 'z'):
        return RECO_IDENT_OU_MOT_RESERVE()
    elif CARLU in [',', ';', '.', ':', '(', ')', '<', '>', '=', '+', '-', '*', '/']:
        return RECO_SYMB()
    elif CARLU == '':
        ERREUR(TYPE_ERREUR.LEXICAL, "fin de fichier inattendue")
    else:
        ERREUR(TYPE_ERREUR.LEXICAL, "caractère illégal")


def INITIALISER(chemin_fichier):
    global SOURCE, CARLU, NUM_LIGNE, TABLE_MOTS_RESERVES, TABLE_IDENT
    NUM_LIGNE = 1
    try:
        SOURCE = open(chemin_fichier, 'r', encoding='utf-8')
    except FileNotFoundError:
        print(f"ERREUR: Fichier '{chemin_fichier}' non trouvé", file=sys.stderr)
        sys.exit(1)
    TABLE_MOTS_RESERVES = [
        'CONST',
        'DEBUT',
        'ECRIRE',
        'FIN',
        'LIRE',
        'PROGRAMME',
        'VAR'
    ]
    TABLE_IDENT = TableIdentificateurs()  # Réinitialiser la table
    LIRE_CAR()


def TERMINER():
    global SOURCE
    if SOURCE is not None:
        SOURCE.close()
        SOURCE = None


# 6. PROGRAMME PRINCIPAL

if __name__ == "__main__":
    # Chemin du fichier source mini-Pascal
    CHEMIN_SOURCE = r"C:\Users\Syssou\Desktop\compilation\Code.minipascal"
    
    # Initialisation
    INITIALISER(CHEMIN_SOURCE)
    
    print("=" * 70)
    print("ANALYSE LEXICALE DU PROGRAMME MINI-PASCAL")
    print("=" * 70)
    print(f"{'LIGNE':<8} {'UNILEX':<15} {'VALEUR':<40}")
    print("-" * 70)
    
    # Analyse lexicale complète
    while True:
        unilex = ANALEX()
        
        # Affichage des tokens reconnus
        if unilex == T_UNILEX.motcle:
            print(f"{NUM_LIGNE:<8} MOTCLE          {CHAINE:<40}")
        elif unilex == T_UNILEX.ident:
            print(f"{NUM_LIGNE:<8} IDENT          {CHAINE:<40}")
        elif unilex == T_UNILEX.ent:
            print(f"{NUM_LIGNE:<8} ENT            {NOMBRE:<40}")
        elif unilex == T_UNILEX.ch:
            print(f"{NUM_LIGNE:<8} CH             '{CHAINE}'{' ' * (38 - len(CHAINE))}")
        elif unilex == T_UNILEX.virg:
            print(f"{NUM_LIGNE:<8} VIRG           ','{' ' * 37}")
        elif unilex == T_UNILEX.ptvirg:
            print(f"{NUM_LIGNE:<8} PTVIRG         ';'{' ' * 37}")
        elif unilex == T_UNILEX.point:
            print(f"{NUM_LIGNE:<8} POINT          '.'{' ' * 37}")
            break
        elif unilex == T_UNILEX.deuxpts:
            print(f"{NUM_LIGNE:<8} DEUXPTS        ':'{' ' * 37}")
        elif unilex == T_UNILEX.parouv:
            print(f"{NUM_LIGNE:<8} PAROUV         '('{' ' * 37}")
        elif unilex == T_UNILEX.parfer:
            print(f"{NUM_LIGNE:<8} PARFER         ')'{' ' * 37}")
        elif unilex == T_UNILEX.inf:
            print(f"{NUM_LIGNE:<8} INF            '<'{' ' * 37}")
        elif unilex == T_UNILEX.sup:
            print(f"{NUM_LIGNE:<8} SUP            '>'{' ' * 37}")
        elif unilex == T_UNILEX.eg:
            print(f"{NUM_LIGNE:<8} EG             '='{' ' * 37}")
        elif unilex == T_UNILEX.plus:
            print(f"{NUM_LIGNE:<8} PLUS           '+'{' ' * 37}")
        elif unilex == T_UNILEX.moins:
            print(f"{NUM_LIGNE:<8} MOINS          '-'{' ' * 37}")
        elif unilex == T_UNILEX.mult:
            print(f"{NUM_LIGNE:<8} MULT           '*'{' ' * 37}")
        elif unilex == T_UNILEX.divi:
            print(f"{NUM_LIGNE:<8} DIVI           '/'{' ' * 37}")
        elif unilex == T_UNILEX.infe:
            print(f"{NUM_LIGNE:<8} INFE           '<='{' ' * 36}")
        elif unilex == T_UNILEX.supe:
            print(f"{NUM_LIGNE:<8} SUPE           '>='{' ' * 36}")
        elif unilex == T_UNILEX.diff:
            print(f"{NUM_LIGNE:<8} DIFF           '<>'{' ' * 35}")
        elif unilex == T_UNILEX.aff:
            print(f"{NUM_LIGNE:<8} AFF            ':='{' ' * 35}")
    
    print("~" * 70)
    print("Analyse lexicale terminée avec succès")
    print("~" * 70)
    
    # === AFFICHAGE DE LA TABLE DES IDENTIFICATEURS===
    TABLE_IDENT.afficher()
    
    TERMINER()