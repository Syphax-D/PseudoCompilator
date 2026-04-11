#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from enum import Enum

# 1. TYPES

class T_UNILEX(Enum):
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

LONG_MAX_IDENT = 20
LONG_MAX_CHAINE = 50
NB_MOTS_RESERVES = 12
MAXINT = 32767


# 3. STRUCTURE DE LA TABLE DES IDENTIFICATEURS

class EntreeIdent:
    def __init__(self, nom: str):
        self.nom = nom
    
    def __repr__(self):
        return self.nom


class TableIdentificateurs:
    def __init__(self):
        self.entrees = []
    
    def _recherche_dichotomique(self, nom: str):
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
        return (False, gauche)
    
    def rechercher(self, nom: str) -> bool:
        trouve, _ = self._recherche_dichotomique(nom)
        return trouve
    
    def ajouter(self, nom: str):
        existe, pos = self._recherche_dichotomique(nom)
        if not existe:
            self.entrees.insert(pos, EntreeIdent(nom))
    
    def afficher(self):
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

SOURCE = None
CARLU = ''
NOMBRE = 0
CHAINE = ''
NUM_LIGNE = 1

TABLE_MOTS_RESERVES = [
    'ALORS',
    'CONST',
    'DEBUT',
    'ECRIRE',
    'FAIRE',
    'FIN',
    'LIRE',
    'PROGRAMME',
    'SI',
    'SINON',
    'TANTQUE',
    'VAR'
]

TABLE_IDENT = TableIdentificateurs()


# 5. FONCTIONS DE L'ANALYSEUR LEXICAL

def ERREUR(type_erreur: TYPE_ERREUR, message: str):
    global NUM_LIGNE
    print(f"\nERREUR {type_erreur.value} LIGNE {NUM_LIGNE}")
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
    while ('A' <= CARLU <= 'Z') or ('a' <= CARLU <= 'z') or ('0' <= CARLU <= '9') or CARLU == '_':
        if 'a' <= CARLU <= 'z':
            car_maj = chr(ord(CARLU) - 32)
        else:
            car_maj = CARLU
        if longueur < LONG_MAX_IDENT:
            CHAINE += car_maj
            longueur += 1
        LIRE_CAR()
    
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
        return None
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
        'ALORS',
        'CONST',
        'DEBUT',
        'ECRIRE',
        'FAIRE',
        'FIN',
        'LIRE',
        'PROGRAMME',
        'SI',
        'SINON',
        'TANTQUE',
        'VAR'
    ]
    TABLE_IDENT = TableIdentificateurs()
    LIRE_CAR()

def TERMINER():
    global SOURCE
    if SOURCE is not None:
        SOURCE.close()
        SOURCE = None


# PARTIE 3 : SYNTAXE / SEMANTIQUE / GEN CODE / INTERPRETEUR

from dataclasses import dataclass

@dataclass
class Symbole:
    nom: str
    genre: str
    typc: int
    adr: int = -1
    val: int = 0


class TableSymboles:
    def __init__(self):
        self.map = {}

    def existe(self, nom: str) -> bool:
        return nom in self.map

    def get(self, nom: str) -> Symbole | None:
        return self.map.get(nom)

    def ajouter(self, sym: Symbole):
        self.map[sym.nom] = sym

    def items_tries(self):
        for k in sorted(self.map.keys()):
            yield self.map[k]

def afficher_table_symboles():
    print("\n" + "="*60)
    print("TABLE DES SYMBOLES")
    print("="*60)
    print(f"{'Nom':<10}{'Genre':<10}{'Type':<10}{'Adr':<6}{'Val'}")
    for s in SYM.items_tries():
        typ = "ENTIER" if s.typc == 0 else "CHAINE"
        print(f"{s.nom:<10}{s.genre:<10}{typ:<10}{s.adr:<6}{s.val}")


# OPCODES

class OP:
    ADDI = 0
    SOUS = 1
    MULT = 2
    DIVI = 3
    MOIN = 4
    AFFE = 5
    LIRE = 6
    ECRL = 7
    ECRE = 8
    ECRC = 9
    FINC = 10
    EMPI = 11
    CONT = 12
    STOP = 13
    ALLE = 14
    ALSN = 15

OPNAME = {
    OP.ADDI: "ADDI", OP.SOUS: "SOUS", OP.MULT: "MULT", OP.DIVI: "DIVI", OP.MOIN: "MOIN",
    OP.AFFE: "AFFE", OP.LIRE: "LIRE", OP.ECRL: "ECRL", OP.ECRE: "ECRE",
    OP.ECRC: "ECRC", OP.FINC: "FINC", OP.EMPI: "EMPI", OP.CONT: "CONT", OP.STOP: "STOP",
    OP.ALLE: "ALLE", OP.ALSN: "ALSN"
}


# VARIABLES GLOBALES PARTIE

UNILEX = None
SYM = TableSymboles()
DERNIERE_ADRESSE_VAR_GLOB = -1
VAL_DE_CONST_CHAINE = [""]
NB_CONST_CHAINE = 0
P_CODE = []
PILOP = []
NOM_FICHIER_SOURCE = ""


# OUTILS PARSER

def avancer():
    global UNILEX
    UNILEX = ANALEX()
    if UNILEX is None:
        UNILEX = T_UNILEX.point

def erreur_syn(msg: str):
    ERREUR(TYPE_ERREUR.SYNTAXIQUE, msg)

def erreur_sem(msg: str):
    ERREUR(TYPE_ERREUR.SEMANTIQUE, msg)

def attendre(tok: T_UNILEX, valeur_motcle: str | None = None):
    global UNILEX, CHAINE
    if UNILEX != tok:
        erreur_syn(f"{tok.name} attendu, trouvé {UNILEX.name}")
    if tok == T_UNILEX.motcle and valeur_motcle is not None:
        if CHAINE != valeur_motcle:
            erreur_syn(f"mot-clé {valeur_motcle} attendu, trouvé {CHAINE}")
    avancer()

def est_motcle(m: str) -> bool:
    return UNILEX == T_UNILEX.motcle and CHAINE == m


# GENERATION DE CODE

def emit(op: int):
    P_CODE.append(op)

def emit_op_arg(op: int, arg: int):
    P_CODE.append(op)
    P_CODE.append(arg)

def emit_ecrc_string(s: str):
    emit(OP.ECRC)
    for ch in s:
        P_CODE.append(ord(ch))
    emit(OP.FINC)

def patch(pos: int, val: int):
    """Corrige l'argument d'une instruction déjà émise à la position pos."""
    P_CODE[pos] = val


# SEMANTIQUE

def definir_constante(nom: str, token_val: T_UNILEX):
    global NB_CONST_CHAINE, VAL_DE_CONST_CHAINE
    if SYM.existe(nom):
        erreur_sem(f"identificateur déjà déclaré: {nom}")
    if token_val == T_UNILEX.ent:
        SYM.ajouter(Symbole(nom=nom, genre="const", typc=0, val=NOMBRE))
    elif token_val == T_UNILEX.ch:
        NB_CONST_CHAINE += 1
        VAL_DE_CONST_CHAINE.append(CHAINE)
        SYM.ajouter(Symbole(nom=nom, genre="const", typc=1, val=NB_CONST_CHAINE))
    else:
        erreur_sem("constante doit être ENT ou CH")

def definir_variable(nom: str):
    global DERNIERE_ADRESSE_VAR_GLOB
    if SYM.existe(nom):
        erreur_sem(f"identificateur déjà déclaré: {nom}")
    DERNIERE_ADRESSE_VAR_GLOB += 1
    SYM.ajouter(Symbole(nom=nom, genre="var", typc=0, adr=DERNIERE_ADRESSE_VAR_GLOB))

def exiger_var(nom: str) -> Symbole:
    s = SYM.get(nom)
    if s is None:
        erreur_sem(f"identificateur non déclaré: {nom}")
    if s.genre != "var":
        erreur_sem(f"{nom} doit être une variable")
    return s

def exiger_decl(nom: str) -> Symbole:
    s = SYM.get(nom)
    if s is None:
        erreur_sem(f"identificateur non déclaré: {nom}")
    return s

def exiger_entier(sym: Symbole, contexte: str):
    if sym.typc != 0:
        erreur_sem(f"type incompatible ({contexte}) : {sym.nom} n'est pas entier")


# PARSER

def PROG():
    attendre(T_UNILEX.motcle, "PROGRAMME")
    if UNILEX != T_UNILEX.ident:
        erreur_syn("identificateur du programme attendu")
    nom_prog = CHAINE
    avancer()
    attendre(T_UNILEX.ptvirg)
    if est_motcle("CONST"):
        DECL_CONST()
    if est_motcle("VAR"):
        DECL_VAR()
    BLOC()
    attendre(T_UNILEX.point)
    emit(OP.STOP)
    return nom_prog

def DECL_CONST():
    attendre(T_UNILEX.motcle, "CONST")
    if UNILEX != T_UNILEX.ident:
        erreur_syn("identificateur attendu après CONST")
    while True:
        nom = CHAINE
        avancer()
        attendre(T_UNILEX.eg)
        if UNILEX not in (T_UNILEX.ent, T_UNILEX.ch):
            erreur_syn("ENT ou CH attendu dans déclaration de constante")
        token_val = UNILEX
        definir_constante(nom, token_val)
        avancer()
        if UNILEX == T_UNILEX.virg:
            avancer()
            if UNILEX != T_UNILEX.ident:
                erreur_syn("identificateur attendu après ',' dans CONST")
            continue
        break
    attendre(T_UNILEX.ptvirg)

def DECL_VAR():
    attendre(T_UNILEX.motcle, "VAR")
    if UNILEX != T_UNILEX.ident:
        erreur_syn("identificateur attendu après VAR")
    while True:
        nom = CHAINE
        definir_variable(nom)
        avancer()
        if UNILEX == T_UNILEX.virg:
            avancer()
            if UNILEX != T_UNILEX.ident:
                erreur_syn("identificateur attendu après ',' dans VAR")
            continue
        break
    attendre(T_UNILEX.ptvirg)

def BLOC():
    attendre(T_UNILEX.motcle, "DEBUT")
    INSTRUCTION()
    while UNILEX == T_UNILEX.ptvirg:
        avancer()
        if est_motcle("FIN"):
            break
        INSTRUCTION()
    attendre(T_UNILEX.motcle, "FIN")

def INSTRUCTION():
    if est_motcle("SI"):
        INST_COND()
    else:
        INST_NON_COND()

def INST_NON_COND():
    if UNILEX == T_UNILEX.ident:
        AFFECTATION()
    elif est_motcle("LIRE"):
        LECTURE()
    elif est_motcle("ECRIRE"):
        ECRITURE()
    elif est_motcle("DEBUT"):
        BLOC()
    elif est_motcle("TANTQUE"):
        INST_REPE()
    else:
        erreur_syn("instruction attendue (IDENT, LIRE, ECRIRE, DEBUT ou TANTQUE)")

def INST_REPE():
    # mémoriser l'adresse de début de la boucle
    PILOP.append(len(P_CODE))

    attendre(T_UNILEX.motcle, "TANTQUE")

    # génère le code de la condition
    EXP()

    # émettre ALSN avec adresse inconnue pour l'instant
    emit_op_arg(OP.ALSN, 0)
    # mémoriser la position de l'argument de ALSN
    PILOP.append(len(P_CODE) - 1)

    attendre(T_UNILEX.motcle, "FAIRE")

    # génère le code de l'instruction/bloc
    INSTRUCTION()

    # dépiler : position arg ALSN et adresse début boucle
    adr_debut = PILOP.pop()
    adr_tantque = PILOP.pop()

    # saut inconditionnel vers le début de la boucle
    emit_op_arg(OP.ALLE, adr_tantque)

    # patcher ALSN avec l'adresse de sortie de boucle
    patch(adr_debut, len(P_CODE))

def INST_COND():
    attendre(T_UNILEX.motcle, "SI")

    # génère le code de la condition
    EXP()

    # émettre ALSN avec adresse inconnue
    emit_op_arg(OP.ALSN, 0)
    pos_alsn = len(P_CODE) - 1

    attendre(T_UNILEX.motcle, "ALORS")

    # génère le code du bloc ALORS
    INST_NON_COND()

    if est_motcle("SINON"):
        # émettre ALLE pour sauter le bloc SINON
        emit_op_arg(OP.ALLE, 0)
        pos_alle = len(P_CODE) - 1

        # patcher ALSN => début du bloc SINON
        patch(pos_alsn, len(P_CODE))

        avancer()  # consommer SINON

        # génère le code du bloc SINON
        INSTRUCTION()

        # patcher ALLE => après le bloc SINON
        patch(pos_alle, len(P_CODE))

    else:
        # pas de SINON => patcher ALSN directement
        patch(pos_alsn, len(P_CODE))

def AFFECTATION():
    if UNILEX != T_UNILEX.ident:
        erreur_syn("identificateur attendu en affectation")
    nom = CHAINE
    s = exiger_var(nom)
    exiger_entier(s, "affectation")
    emit_op_arg(OP.EMPI, s.adr)
    avancer()
    attendre(T_UNILEX.aff)
    EXP()
    emit(OP.AFFE)

def LECTURE():
    attendre(T_UNILEX.motcle, "LIRE")
    attendre(T_UNILEX.parouv)
    if UNILEX != T_UNILEX.ident:
        erreur_syn("identificateur attendu dans LIRE(")
    while True:
        nom = CHAINE
        s = exiger_var(nom)
        exiger_entier(s, "lecture")
        emit_op_arg(OP.EMPI, s.adr)
        emit(OP.LIRE)
        avancer()
        if UNILEX == T_UNILEX.virg:
            avancer()
            if UNILEX != T_UNILEX.ident:
                erreur_syn("identificateur attendu après ',' dans LIRE")
            continue
        break
    attendre(T_UNILEX.parfer)

def ECRITURE():
    attendre(T_UNILEX.motcle, "ECRIRE")
    attendre(T_UNILEX.parouv)
    if UNILEX == T_UNILEX.parfer:
        avancer()
        emit(OP.ECRL)
        return
    ECR_EXP()
    while UNILEX == T_UNILEX.virg:
        avancer()
        ECR_EXP()
    attendre(T_UNILEX.parfer)

def ECR_EXP():
    if UNILEX == T_UNILEX.ch:
        emit_ecrc_string(CHAINE)
        avancer()
    else:
        EXP()
        emit(OP.ECRE)

def EXP():
    TERME()
    SUITE_TERME()

def SUITE_TERME():
    if UNILEX in (T_UNILEX.plus, T_UNILEX.moins, T_UNILEX.mult, T_UNILEX.divi):
        OP_BIN()
        EXP()
        op = PILOP.pop()
        emit(op)

def OP_BIN():
    if UNILEX == T_UNILEX.plus:
        PILOP.append(OP.ADDI)
    elif UNILEX == T_UNILEX.moins:
        PILOP.append(OP.SOUS)
    elif UNILEX == T_UNILEX.mult:
        PILOP.append(OP.MULT)
    elif UNILEX == T_UNILEX.divi:
        PILOP.append(OP.DIVI)
    else:
        erreur_syn("opérateur binaire attendu (+ - * /)")
    avancer()

def TERME():
    if UNILEX == T_UNILEX.ent:
        emit_op_arg(OP.EMPI, NOMBRE)
        avancer()
        return
    if UNILEX == T_UNILEX.ident:
        nom = CHAINE
        s = exiger_decl(nom)
        exiger_entier(s, "expression")
        if s.genre == "var":
            emit_op_arg(OP.EMPI, s.adr)
            emit(OP.CONT)
        else:
            emit_op_arg(OP.EMPI, s.val)
        avancer()
        return
    if UNILEX == T_UNILEX.parouv:
        avancer()
        EXP()
        attendre(T_UNILEX.parfer)
        return
    if UNILEX == T_UNILEX.moins:
        avancer()
        TERME()
        emit(OP.MOIN)
        return
    erreur_syn("terme attendu (ENT, IDENT, '(', ou '-')")


# FICHIER .COD

def creer_fichier_code(nom_prog: str, fichier_source: str):
    base = fichier_source
    if base.lower().endswith(".mp") or base.lower().endswith(".minipascal") or base.lower().endswith(".txt"):
        base = base.rsplit(".", 1)[0]
    path = base + ".COD"
    i = 0
    with open(path, "w", encoding="utf-8") as f:
        nb_vars = DERNIERE_ADRESSE_VAR_GLOB + 1
        f.write(f"{nb_vars}\n")
        while i < len(P_CODE):
            op = P_CODE[i]
            name = OPNAME.get(op, f"OP_{op}")
            if op == OP.EMPI:
                arg = P_CODE[i+1]
                f.write(f"{name} {arg}\n")
                i += 2
            elif op == OP.ECRC:
                f.write("ECRC ")
                i += 1
                while i < len(P_CODE) and P_CODE[i] != OP.FINC:
                    f.write(chr(P_CODE[i]))
                    i += 1
                f.write(" FINC\n")
                i += 1
            elif op in (OP.ALLE, OP.ALSN):
                arg = P_CODE[i + 1]
                f.write(f"{name} {arg}\n")
                i += 2
            else:
                f.write(f"{name}\n")
                i += 1
    print(f"[OK] Fichier code généré: {path}")


# INTERPRETEUR MACHINE VIRTUELLE

def afficher_pcode():
    print("\n" + "="*60)
    print("P_CODE GENERE")
    print("="*60)
    i = 0
    while i < len(P_CODE):
        op = P_CODE[i]
        nom = OPNAME.get(op, str(op))
        if op == OP.EMPI:
            print(nom, P_CODE[i+1])
            i += 2
        elif op == OP.ECRC:
            texte = ""
            i += 1
            while P_CODE[i] != OP.FINC:
                texte += chr(P_CODE[i])
                i += 1
            print("ECRC", texte)
            i += 1
        elif op in (OP.ALLE, OP.ALSN):
            arg = P_CODE[i + 1]
            print(f"{nom} {arg}")
            i += 2
        else:
            print(nom)
            i += 1

def interpreter():
    nb_vars = DERNIERE_ADRESSE_VAR_GLOB + 1
    MEMVAR = [0] * max(nb_vars, 1)
    PILEX = [0] * 10000
    SOM = -1
    co = 0

    def pop():
        nonlocal SOM
        if SOM < 0:
            raise RuntimeError("pile vide")
        v = PILEX[SOM]
        SOM -= 1
        return v

    def push(v: int):
        nonlocal SOM
        SOM += 1
        if SOM >= len(PILEX):
            raise RuntimeError("pile pleine")
        PILEX[SOM] = v

    while True:
        op = P_CODE[co]

        if op == OP.ADDI:
            b = pop(); a = pop()
            push(a + b)
            co += 1
        elif op == OP.SOUS:
            b = pop(); a = pop()
            push(a - b)
            co += 1
        elif op == OP.MULT:
            b = pop(); a = pop()
            push(a * b)
            co += 1
        elif op == OP.DIVI:
            b = pop(); a = pop()
            if b == 0:
                raise RuntimeError("division par zéro")
            push(a // b)
            co += 1
        elif op == OP.MOIN:
            a = pop()
            push(-a)
            co += 1
        elif op == OP.EMPI:
            arg = P_CODE[co + 1]
            push(arg)
            co += 2
        elif op == OP.CONT:
            adr = pop()
            push(MEMVAR[adr])
            co += 1
        elif op == OP.AFFE:
            val = pop()
            adr = pop()
            MEMVAR[adr] = val
            co += 1
        elif op == OP.LIRE:
            adr = pop()
            try:
                v = int(input())
            except ValueError:
                raise RuntimeError("entrée invalide")
            MEMVAR[adr] = v
            co += 1
        elif op == OP.ECRL:
            print()
            co += 1
        elif op == OP.ECRE:
            val = pop()
            print(val, end="")
            co += 1
        elif op == OP.ECRC:
            co += 1
            while P_CODE[co] != OP.FINC:
                print(chr(P_CODE[co]), end="")
                co += 1
            co += 1
        elif op == OP.STOP:
            break
        elif op == OP.ALLE:
            co = P_CODE[co + 1]
        elif op == OP.ALSN:
            arg = P_CODE[co + 1]
            val = pop()        # dépiler la valeur testée
            if val == 0:       # si nul => sauter
                co = arg
            else:
                co += 2
        else:
            raise RuntimeError(f"opcode inconnu: {op}")


# POINT D'ENTREE COMPILATION + EXECUTION

def compiler_et_executer(fichier_source: str, executer=True, generer_cod=True):
    global NOM_FICHIER_SOURCE, SYM, DERNIERE_ADRESSE_VAR_GLOB, VAL_DE_CONST_CHAINE, NB_CONST_CHAINE
    global P_CODE, PILOP, UNILEX

    NOM_FICHIER_SOURCE = fichier_source
    SYM = TableSymboles()
    DERNIERE_ADRESSE_VAR_GLOB = -1
    VAL_DE_CONST_CHAINE = [""]
    NB_CONST_CHAINE = 0
    P_CODE = []
    PILOP = []
    print("Fichier analysé :", fichier_source)

    INITIALISER(fichier_source)
    avancer()

    nom_prog = PROG()
    TERMINER()

    if generer_cod:
        creer_fichier_code(nom_prog, fichier_source)

    if executer:
        interpreter()

    print("\nCompilation terminée.")


if __name__ == "__main__":

    CHEMIN_SOURCE = r"../compilation/Code.minipascal"

    print("\n~~~~~~~~~~~~~ Analyse lexicale ~~~~~~~~~~~~~\n")

    INITIALISER(CHEMIN_SOURCE)

    print(f"{'LIGNE':<8} {'TOKEN':<15} {'VALEUR'}")
    print("-"*50)

    while True:
        tok = ANALEX()
        if tok is None:
            break
        if tok == T_UNILEX.motcle:
            print(NUM_LIGNE, " MOTCLE ", CHAINE)
        elif tok == T_UNILEX.ident:
            print(NUM_LIGNE, " IDENT ", CHAINE)
        elif tok == T_UNILEX.ent:
            print(NUM_LIGNE, " ENT ", NOMBRE)
        elif tok == T_UNILEX.ch:
            print(NUM_LIGNE, " CH ", CHAINE)
        elif tok == T_UNILEX.aff:
            print(NUM_LIGNE, " :=")
        elif tok == T_UNILEX.plus:
            print(NUM_LIGNE, " +")
        elif tok == T_UNILEX.mult:
            print(NUM_LIGNE, " *")
        elif tok == T_UNILEX.ptvirg:
            print(NUM_LIGNE, " ;")
        elif tok == T_UNILEX.virg:
            print(NUM_LIGNE, " ,")
        elif tok == T_UNILEX.parouv:
            print(NUM_LIGNE, " (")
        elif tok == T_UNILEX.parfer:
            print(NUM_LIGNE, " )")
        elif tok == T_UNILEX.point:
            print(NUM_LIGNE, " .")
            break

    TERMINER()

    compiler_et_executer(
        CHEMIN_SOURCE,
        executer=False,
        generer_cod=True
    )

    print("\n~~~~~~~~~~~~~ Table des symboles ~~~~~~~~~~~~~~\n")
    afficher_table_symboles()

    print("\n~~~~~~~~~~~~~ P_CODE ~~~~~~~~~~~~~~\n")
    afficher_pcode()

    print("\n~~~~~~~~~~~~~ Execution ~~~~~~~~~~~~~~\n")
    interpreter()

    print("\n~~~~~~~~~~~~~ FIN ~~~~~~~~~~~~~~\n")