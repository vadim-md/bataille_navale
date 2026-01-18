import random
from tkinter import *
from placement_tir import gestion_tir
from placement_bateaux_sur_grille import CASE, TAILLE_GRILLE, Jeu
import csv 
import os

accueil = Tk()

# Titre
Label(accueil, text="Bataille navale").place(x=650, y=200)




def charger_score():
    if not os.path.exists("scores.csv"):#si le fichier existe pas on en creer un
        with open("scores.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["joueur", "bot"])
            writer.writerow([0, 0])
        return 0, 0

    with open("scores.csv", "r") as f:
        reader = csv.reader(f)
        next(reader)  # sauter l'en-tête
        joueur, bot = next(reader)
        return int(joueur), int(bot)

def sauvegarder_score(joueur, bot):
    with open("scores.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["joueur", "bot"])
        writer.writerow([joueur, bot])


score_joueur, score_bot = charger_score()

# Image de fond
canvas = Canvas(accueil, width=1600, height=1143)
canvas.place(x=0, y=0)
fond = PhotoImage(file="fond.png")
canvas.create_image(650, 0, anchor="n", image=fond)

# Titre visible
Label(accueil, text="Bataille navale", bg="lightblue", font=("Arial", 50)).place(x=430, y=200, width=600, height=100)

# Historique des tirs
historique_tirs_joueur = set()  # tir humain sur le bot
historique_tirs_bot = set()     # tir bot sur le joueur
partie_terminee = False

terrain_adversaire = None
terrain_joueur = None


label_score = Label(
    accueil,
    text=f"Score  Joueur : {score_joueur}  |  Bot : {score_bot}",
    font=("Arial", 18),
    bg="lightyellow"
)
label_score.place(x=500, y=320)





def tir_effectue(event=None):
    global partie_terminee
    if partie_terminee:
        return

    #tir humain
    x, y = terrain_adversaire.pos_tir
    historique_tirs_joueur.add((x, y))
    verifier(terrain_adversaire.grille_occupee)

    if verifier_victoire():
        return

    
    action_bot()


def verifier_victoire():
    global partie_terminee

    if partie_terminee:
        return True

    #regarde si tout les bateaux de la grille joueur on etais touche
    joueur_perdu = True
    for elem in terrain_joueur.positions:
        for k in range(elem[3]):
            x = elem[0] + k if elem[2] == 'H' else elem[0]
            y = elem[1] if elem[2] == 'H' else elem[1] + k
            if (x, y) not in historique_tirs_bot:
                joueur_perdu = False
                break
        if not joueur_perdu:
            break

    #regarde si tout les bateaux de la grille bot on etais touche
    bot_perdu = True
    for y in range(TAILLE_GRILLE):
        for x in range(TAILLE_GRILLE):
            if terrain_adversaire.grille_occupee[y][x] == 1:
                if (x, y) not in historique_tirs_joueur:
                    bot_perdu = False
                    break
        if not bot_perdu:
            break

    #option egalité (a supprimer pt)
    if not joueur_perdu and not bot_perdu:
        return False

    
    partie_terminee = True
    global score_joueur, score_bot

    if joueur_perdu:
        score_bot += 1
    else:
        score_joueur += 1

    sauvegarder_score(score_joueur, score_bot)

    label_score.config(
    text=f"Score  Joueur : {score_joueur}  |  Bot : {score_bot}"
    )


    # centralise le bouton victoire\defaites
    x_centre = 20 + (TAILLE_GRILLE * CASE) + (800 - (20 + TAILLE_GRILLE * CASE)) // 2
    y_centre = 400 + (TAILLE_GRILLE * CASE) // 2

    frame_fin = Frame(accueil, bg="lightgrey", bd=3, relief="ridge")
    frame_fin.place(anchor="center", x=x_centre, y=y_centre)

    message = "LE BOT EST PLUS FORT" if joueur_perdu else "VICTOIRE"
    couleur = "red" if joueur_perdu else "green"

    Label(
        frame_fin,
        text=message,
        bg=couleur,
        fg="white",
        font=("Arial", 30),
        padx=20,
        pady=10
        ).pack(pady=(10, 5))

    
    
    Button(
        frame_fin,
        text="Recommencer",
        font=("Arial", 15),
        bg="lightblue",
        command=lambda: [frame_fin.destroy(), recommencer_partie()],
            padx=20
        ).pack(pady=(5, 10))


    Button(
        frame_fin,
        text="Quitter",
        font=("Arial", 15),
        bg="orange",
        command=accueil.quit,
        padx=20
        ).pack(pady=(5, 15))


    # désactiver les boutons du joueur
    for bouton in [terrain_joueur.bouton2, terrain_joueur.bouton3,
                   terrain_joueur.bouton4, terrain_joueur.bouton5]:
        try:
            bouton.config(state=DISABLED)
        except:
            pass

    return True


def recommencer_partie():
    #reutilise les autres fonction pour recreer 
    global partie_terminee
    global historique_tirs_joueur, historique_tirs_bot

    partie_terminee = False
    historique_tirs_joueur.clear()
    historique_tirs_bot.clear()

    # Effacer les anciennes grilles
    terrain_joueur.zone.destroy()
    terrain_adversaire.zone.destroy()

    # Recréer les plateaux
    terrain_joueur.plateau(accueil)
    terrain_adversaire.plateau(accueil)

    # Replacer les bateaux
    terrain_adversaire.grille_occupee = placement_bateau_bot()

    # Réactiver les boutons joueur (si DISABLE)
    try:
        terrain_joueur.bouton2.config(state=NORMAL)
        terrain_joueur.bouton3.config(state=NORMAL)
        terrain_joueur.bouton4.config(state=NORMAL)
        terrain_joueur.bouton5.config(state=NORMAL)
    except:
        pass



def notif_bateaux_valides():
    terrain_adversaire.bouger_tir()


terrain_adversaire = gestion_tir(accueil, tir_effectue)
terrain_joueur = Jeu(accueil, notif_bateaux_valides)


def action_bot():
    if partie_terminee:
        return

    # Tir bot aléatoire
    while True:
        x_case = random.randint(0, TAILLE_GRILLE - 1)
        y_case = random.randint(0, TAILLE_GRILLE - 1)
        if (x_case, y_case) not in historique_tirs_bot:
            break
    #permet de savoir la pos des tirs du bot et du joueur 
    historique_tirs_bot.add((x_case, y_case))
    terrain_joueur.pos_tir = [x_case, y_case]
    verifier(terrain_joueur.grille_occupee)
    verifier_victoire()


def verifier(grille_occupee, event=None):
    # Déterminer si le tir touche ou dans l'eau
    in_water = True
    for elem in terrain_joueur.positions:
        if elem[2] == 'H':
            if elem[1] == terrain_joueur.pos_tir[1] and elem[0] <= terrain_joueur.pos_tir[0] < elem[0] + elem[3]:
                in_water = False
        else:
            if elem[0] == terrain_joueur.pos_tir[0] and elem[1] <= terrain_joueur.pos_tir[1] < elem[1] + elem[3]:
                in_water = False

    # Affichage sur plateau joueur
    couleur = "white" if in_water else "red"
    label_text = "Plouf" if in_water else "Touché"
    Label(terrain_joueur.fen, text=label_text, bg="grey" if in_water else "red").place(x=450, y=350)
    terrain_joueur.zone.create_rectangle(
        terrain_joueur.pos_tir[0] * CASE,
        terrain_joueur.pos_tir[1] * CASE,
        terrain_joueur.pos_tir[0] * CASE + CASE,
        terrain_joueur.pos_tir[1] * CASE + CASE,
        fill=couleur
    )

    # Affichage sur plateau bot
    x, y = terrain_adversaire.pos_tir
    in_water_bot = True
    if terrain_adversaire.grille_occupee[y][x] == 1:
        in_water_bot = False
    couleur_bot = "white" if in_water_bot else "red"
    label_text_bot = "Plouf" if in_water_bot else "Touché"
    Label(terrain_adversaire.plateau_adversaire, text=label_text_bot, bg="grey" if in_water_bot else "red").place(x=850, y=350)
    terrain_adversaire.zone.create_rectangle(
        x * CASE,
        y * CASE,
        x * CASE + CASE,
        y * CASE + CASE,
        fill=couleur_bot
    )
    #
    terrain_joueur.pos_tir = [0, 0]
    terrain_adversaire.pos_tir = [0, 0]
    terrain_adversaire.tour_suivant()
    return in_water, [x, y]


def commencer():
    bouton1.destroy()
    generer_partie()
    terrain_adversaire.grille_occupee = placement_bateau_bot()


def generer_partie():
    terrain_adversaire.plateau(accueil)
    terrain_joueur.plateau(accueil)


bouton1 = Button(accueil, text="Commencer", command=commencer)
bouton1.place(x=650, y=450)
Button(accueil, text="Quitter", command=accueil.quit).place(x=665, y=100)


def placement_bateau_bot():
    taille_bateau = [2, 3, 4, 5]
    grille_occupee = [[0 for _ in range(TAILLE_GRILLE)] for _ in range(TAILLE_GRILLE)]
    for elem in taille_bateau:
        placer = False
        while not placer:
            longueur = elem
            sens = random.randint(1, 2)
            if sens == 1:  # Horizontale
                orientation = "H"
                y = random.randint(0, TAILLE_GRILLE - 1)
                x = random.randint(0, TAILLE_GRILLE - longueur)
            else:  # Verticale
                orientation = "V"
                x = random.randint(0, TAILLE_GRILLE - 1)
                y = random.randint(0, TAILLE_GRILLE - longueur)
            if not terrain_joueur.chevauchement(grille_occupee, x, y, orientation, longueur):
                for k in range(longueur):
                    i = x + k if orientation == "H" else x
                    j = y if orientation == "H" else y + k
                    grille_occupee[j][i] = 1
                    terrain_adversaire.zone.create_rectangle(
                        i * CASE,
                        j * CASE,
                        (i + 1) * CASE,
                        (j + 1) * CASE,
                        state='hidden'
                    )
                placer = True
    return grille_occupee



accueil.mainloop()
