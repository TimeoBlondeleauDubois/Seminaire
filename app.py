from flask import Flask, render_template, request, redirect, url_for, session
from bcrypt import hashpw, gensalt
import sqlite3, random
from datetime import datetime
from flask import flash

app = Flask(__name__)
app.secret_key = 'b_5#y2L"F4Q8z\n\xec]/'

connection = sqlite3.connect('Pendu.db')
cursor = connection.cursor()

@app.route('/')
def home():
    return render_template('login.html')

def connect_db():
    db_path = 'Pendu.db'
    print(f"Connecté à la base de données : {db_path}")
    return sqlite3.connect(db_path)

#Se connecter
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_credentials(username, password):
            return redirect(url_for('dashboard'))
        else:
            error = 'Nom d\'utilisateur ou mot de passe incorrect'
    return render_template('login.html', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Avant create_user: {username}, {password}")
        if create_user(username, password):
            print("Après create_user: Utilisateur créé avec succès")
            return redirect(url_for('login'))
        else:
            error = 'Nom d\'utilisateur déjà pris'
    return render_template('signup.html', error=error)

#Dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('difficulty.html')

def check_credentials(username, password):
    with connect_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT US_Id, Mot_De_Passe FROM User WHERE Nom_Utilisateur = ?", (username,))
        user_data = cursor.fetchone()

    if user_data is not None:
        user_id, stored_password = user_data
        if hashpw(password.encode('utf-8'), stored_password) == stored_password:
            session['user_id'] = user_id
            return user_id
    return None

#Creer un joueur
def create_user(username, password):
    try:
        hashed_password = hashpw(password.encode('utf-8'), gensalt())
        with connect_db() as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO User (Nom_Utilisateur, Mot_De_Passe) VALUES (?, ?)", (username, hashed_password))
        print(f"Utilisateur {username} créé avec succès")
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la création de l'utilisateur : {e}")
        return False

@app.route('/dashboard', methods=['GET', 'POST'])
def choose_difficulty():
    reinitialiser_jeu()
    if request.method == 'POST':
        difficulty = request.form['difficulty']
        return redirect(url_for('game', difficulty=difficulty))
    else:
        return render_template('difficulty.html')

#Difficulté
@app.route('/game/<difficulty>')
def game(difficulty):
    if 'mot_a_deviner' not in session:
        session['mot_a_deviner'] = choisir_mot(difficulty)
        session['lettres_trouvees'] = []
        session['tentatives_restantes'] = 6
        session['difficulty'] = difficulty
        session.pop('message_fin', None)
        session['Date_Du_Jeu'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    resultat = afficher_mot_cache(session['mot_a_deviner'], session['lettres_trouvees'])
    message = "" # Pour mettre un message
    tentatives_restantes = session['tentatives_restantes']
    lettres_trouvees = session['lettres_trouvees']

    return render_template('game.html', resultat=resultat, message=message, tentatives_restantes=tentatives_restantes, lettres_trouvees=lettres_trouvees)

#Pendu
def choisir_mot(difficulty):
    with connect_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT Mot FROM Liste_De_Mots WHERE Difficulty = ? ORDER BY RANDOM() LIMIT 1", (difficulty,))
        mot = cursor.fetchone()

    if mot:
        mot = mot[0].lower()
        print(f"Mot choisi : {mot}")
        return mot
    else:
        print("Aucun mot trouvé dans la base de données.")
        return None
    
#Reset le pendu
def reinitialiser_jeu():
    session.pop('mot_a_deviner', None)
    session.pop('lettres_trouvees', None)
    session.pop('tentatives_restantes', None)
    session.pop('difficulty', None)
    session.pop('message_fin', None)
    session.pop('Date_Du_Jeu', None)
    return redirect(url_for('choose_difficulty'))

def afficher_mot_cache(mot, lettres_trouvees):
    mot_cache = ""
    for lettre in mot:
        if lettre in lettres_trouvees:
            mot_cache += lettre
        else:
            mot_cache += "_"
    return mot_cache

#Pendu1
@app.route("/pendu")
def index():
    if 'mot_a_deviner' not in session:
        session['mot_a_deviner'] = choisir_mot()

    session['lettres_trouvees'] = []
    session['tentatives_restantes'] = 6

    lettres_trouvees = session['lettres_trouvees']
    tentatives_restantes = session['tentatives_restantes']

    mot_cache = afficher_mot_cache(session['mot_a_deviner'], lettres_trouvees)

    print(f"Mot à deviner : {session['mot_a_deviner']}")
    print(f"Lettres trouvées : {lettres_trouvees}")
    print(f"Tentatives restantes : {tentatives_restantes}")

    session.pop('message_fin', None)
    return render_template("game.html", resultat=mot_cache, tentatives_restantes=tentatives_restantes, lettres_trouvees=lettres_trouvees, message="")

#Pendu2
@app.route("/jouer", methods=["POST"])
def jouer():
    if 'mot_a_deviner' not in session:
        session['mot_a_deviner'] = choisir_mot()

    lettre = request.form.get("lettre").lower()

    if 'lettres_trouvees' not in session:
        session['lettres_trouvees'] = []
    if 'tentatives_restantes' not in session:
        session['tentatives_restantes'] = 6

    lettres_trouvees = session['lettres_trouvees']
    tentatives_restantes = session['tentatives_restantes']

    message = ""

    if len(lettre) != 1 or not lettre.isalpha():
        message = "Veuillez entrer une lettre."
    elif lettre in lettres_trouvees:
        message = "Vous avez déjà entré cette lettre. Essayez une autre."
    elif lettre not in session['mot_a_deviner']:
        tentatives_restantes -= 1
        lettres_trouvees.append(lettre)
    else:
        lettres_trouvees.append(lettre)

    session['lettres_trouvees'] = lettres_trouvees
    session['tentatives_restantes'] = tentatives_restantes

    mot_cache = afficher_mot_cache(session['mot_a_deviner'], lettres_trouvees)

    if "_" not in mot_cache or tentatives_restantes == 0:
        session['message_fin'] = message
        return redirect("/fin-de-partie")

    return render_template("game.html", resultat=mot_cache, tentatives_restantes=tentatives_restantes, lettres_trouvees=lettres_trouvees, message=message)

@app.route('/recommencer_une_partie')
def recommencer_une_partie():
    return render_template('difficulty.html')

#Score
@app.route("/fin-de-partie")
def fin_de_partie():
    mot_a_deviner = session.get('mot_a_deviner', '')
    message_fin = session.get('message_fin', '')
    user_id = session.get('user_id')
    difficulty = session.get('difficulty', 'Facile')
    
    Date_Du_Jeu = session.get('Date_Du_Jeu', '')
    
    if "_" not in afficher_mot_cache(mot_a_deviner, session.get('lettres_trouvees', [])):
        resultat = "Gagné"
    else:
        resultat = "Perdu"

    session['resultat'] = resultat
    session['difficulty'] = difficulty
    session['Date_Du_Jeu'] = Date_Du_Jeu

    with connect_db() as db:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO Partie (Date_Du_Jeu, Mot_A_Deviner, Gagne_Facile, Perdu_Facile, Gagne_Moyen, Perdu_Moyen, 
                               Gagne_Difficile, Perdu_Difficile, Resultat, Difficulty, User_Id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (Date_Du_Jeu, mot_a_deviner, int(difficulty == 'Facile' and resultat == 'Gagné'),
              int(difficulty == 'Facile' and resultat == 'Perdu'), int(difficulty == 'Moyen' and resultat == 'Gagné'),
              int(difficulty == 'Moyen' and resultat == 'Perdu'), int(difficulty == 'Difficile' and resultat == 'Gagné'),
              int(difficulty == 'Difficile' and resultat == 'Perdu'), resultat, difficulty, user_id))

        if resultat == "Gagné":
            update_column = f'Gagne_{difficulty}'
        else:
            update_column = f'Perdu_{difficulty}'
        
        cursor.execute(f"UPDATE Partie SET {update_column} = {update_column} + 1 WHERE User_Id = ? AND Partie_Id = ?",
                       (user_id, cursor.lastrowid))

    return redirect(url_for('afficher_resultat', resultat=resultat, mot_a_deviner=mot_a_deviner, message_fin=message_fin, difficulty=difficulty))

@app.route('/afficher_resultat')
def afficher_resultat():
    resultat = session.get('resultat', '')
    mot_a_deviner = session.get('mot_a_deviner', '')
    message_fin = session.get('message_fin', '')
    difficulty = session.get('difficulty', '')

    return render_template('fin_de_partie.html', resultat=resultat, mot_a_deviner=mot_a_deviner, message_fin=message_fin, difficulty=difficulty)

#Déconnexion
@app.route('/logout')
def logout():
    session.pop('mot_a_deviner', None)
    session.pop('lettres_trouvees', None)
    session.pop('tentatives_restantes', None)
    session.pop('difficulty', None)
    session.pop('message_fin', None)
    session.pop('Date_Du_Jeu', None)
    session.pop('user_id', None)
    session.pop('mot_a_deviner', None)
    session.pop('lettres_trouvees', None)
    session.pop('tentatives_restantes', None)
    session.pop('difficulty', None)
    session.pop('message_fin', None)
    session.pop('Date_Du_Jeu', None)
    session.pop('user_id', None)
    session.pop('game_history_facile', None)
    session.pop('game_history_moyen', None)
    session.pop('game_history_difficile', None)
    session.pop('mot_a_deviner', None)
    session.pop('lettres_trouvees', None)
    session.pop('tentatives_restantes', None)
    session.pop('difficulty', None)
    session.pop('message_fin', None)
    session.pop('Date_Du_Jeu', None)
    session.pop('user_id', None)
    session.pop('game_history_facile', None)
    session.pop('game_history_moyen', None)
    session.pop('game_history_difficile', None)
    session.pop('classement_data', None)
    session.clear()
    return redirect("/")

#Historique et statistique
def get_historique_data(user_id):
    
    #Historique
    with connect_db() as db:
        cursor = db.cursor()
        cursor.execute("""
            SELECT Date_Du_Jeu, Mot_A_Deviner, Resultat
            FROM Partie
            WHERE User_Id = ? AND Difficulty = "facile"
            ORDER BY Date_Du_Jeu DESC;
        """, (user_id,))
        game_history_facile = cursor.fetchall()

    with connect_db() as db:
        cursor = db.cursor()
        cursor.execute("""
            SELECT Date_Du_Jeu, Mot_A_Deviner, Resultat
            FROM Partie
            WHERE User_Id = ? AND Difficulty = "moyen"
            ORDER BY Date_Du_Jeu DESC;
        """, (user_id,))
        game_history_moyen = cursor.fetchall()

    with connect_db() as db:
        cursor = db.cursor()
        cursor.execute("""
            SELECT Date_Du_Jeu, Mot_A_Deviner, Resultat
            FROM Partie
            WHERE User_Id = ? AND Difficulty = "difficile"
            ORDER BY Date_Du_Jeu DESC;
        """, (user_id,))
        game_history_difficile = cursor.fetchall()

    #Statistique
    total_facile = len(game_history_facile)
    pourcentage_facile = round((len([game for game in game_history_facile if game[2] == "Gagné"]) / total_facile) * 100, 2) if total_facile > 0 else 0

    total_moyen = len(game_history_moyen)
    pourcentage_moyen = round((len([game for game in game_history_moyen if game[2] == "Gagné"]) / total_moyen) * 100, 2) if total_moyen > 0 else 0

    total_difficile = len(game_history_difficile)
    pourcentage_difficile = round((len([game for game in game_history_difficile if game[2] == "Gagné"]) / total_difficile) * 100, 2) if total_difficile > 0 else 0

    total_parties = total_facile + total_moyen + total_difficile
    pourcentage_total = round((len([game for game in game_history_facile + game_history_moyen + game_history_difficile if game[2] == "Gagné"]) / total_parties) * 100, 2) if total_parties > 0 else 0

    total_gagne_facile = len([game for game in game_history_facile if game[2] == "Gagné"])
    total_perdu_facile = len([game for game in game_history_facile if game[2] == "Perdu"])

    total_gagne_moyen = len([game for game in game_history_moyen if game[2] == "Gagné"])
    total_perdu_moyen = len([game for game in game_history_moyen if game[2] == "Perdu"])

    total_gagne_difficile = len([game for game in game_history_difficile if game[2] == "Gagné"])
    total_perdu_difficile = len([game for game in game_history_difficile if game[2] == "Perdu"])

    return {
        "game_history_facile": game_history_facile,
        "game_history_moyen": game_history_moyen,
        "game_history_difficile": game_history_difficile,
        "total_facile": total_facile,
        "pourcentage_facile": pourcentage_facile,
        "total_moyen": total_moyen,
        "pourcentage_moyen": pourcentage_moyen,
        "total_difficile": total_difficile,
        "pourcentage_difficile": pourcentage_difficile,
        "total_parties": total_parties,
        "pourcentage_total": pourcentage_total,
        "total_gagne_facile": total_gagne_facile,
        "total_perdu_facile": total_perdu_facile,
        "total_gagne_moyen": total_gagne_moyen,
        "total_perdu_moyen": total_perdu_moyen,
        "total_gagne_difficile": total_gagne_difficile,
        "total_perdu_difficile": total_perdu_difficile
    }

#Classement
def get_classement_data(sort_key):

    #Cas ou total est coché (de base)
    with connect_db() as db:
        cursor = db.cursor()
        if sort_key == 'nom_asc_total':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as Pourcentage_Victoires,
                    (SUM(Gagne_Facile)+SUM(Gagne_Moyen)+SUM(Gagne_Difficile)) as Victoires_total
                FROM Partie
                JOIN User ON Partie.User_Id = User.US_Id
                GROUP BY Nom_Utilisateur
                ORDER BY Nom_Utilisateur ASC;
            """)
        elif sort_key == 'nom_desc_total':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as Pourcentage_Victoires,
                    (SUM(Gagne_Facile)+SUM(Gagne_Moyen)+SUM(Gagne_Difficile)) as Victoires_total
                FROM Partie
                JOIN User ON Partie.User_Id = User.US_Id
                GROUP BY Nom_Utilisateur
                ORDER BY Nom_Utilisateur DESC;
            """)
        elif sort_key == 'victoire_asc_total':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as Pourcentage_Victoires,
                    (SUM(Gagne_Facile)+SUM(Gagne_Moyen)+SUM(Gagne_Difficile)) as Victoires_total
                FROM Partie
                JOIN User ON Partie.User_Id = User.US_Id
                GROUP BY Nom_Utilisateur
                ORDER BY Pourcentage_Victoires DESC;
            """)
        elif sort_key == 'victoire_desc_total':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as Pourcentage_Victoires,
                    (SUM(Gagne_Facile)+SUM(Gagne_Moyen)+SUM(Gagne_Difficile)) as Victoires_total
                FROM Partie
                JOIN User ON Partie.User_Id = User.US_Id
                GROUP BY Nom_Utilisateur
                ORDER BY Pourcentage_Victoires ASC;
            """)
        elif sort_key == 'nombre_de_victoire_total_desc_total':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as Pourcentage_Victoires,
                    (SUM(Gagne_Facile)+SUM(Gagne_Moyen)+SUM(Gagne_Difficile)) as Victoires_total
                FROM 
                    Partie
                JOIN 
                    User ON Partie.User_Id = User.US_Id
                GROUP BY 
                    User.Nom_Utilisateur
                ORDER BY 
                    Victoires_total ASC;
            """)
        elif sort_key == 'nombre_de_victoire_total_asc_total':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as Pourcentage_Victoires,
                    (SUM(Gagne_Facile)+SUM(Gagne_Moyen)+SUM(Gagne_Difficile)) as Victoires_total
                FROM 
                    Partie
                JOIN 
                    User ON Partie.User_Id = User.US_Id
                GROUP BY 
                    User.Nom_Utilisateur
                ORDER BY 
                    Victoires_total DESC;
            """)

        #Cas ou facile est coché
        elif sort_key == 'nom_asc_facile':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' AND Difficulty = 'facile' THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN Difficulty = 'facile' THEN 1 ELSE 0 END), 2) as Pourcentage_Victoires_Facile,
                    SUM(Gagne_Facile) as Victoires_Faciles
                FROM Partie
                JOIN User ON Partie.User_Id = User.US_Id
                GROUP BY Nom_Utilisateur
                ORDER BY Nom_Utilisateur ASC;
            """)
        elif sort_key == 'nom_desc_facile':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' AND Difficulty = 'facile' THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN Difficulty = 'facile' THEN 1 ELSE 0 END), 2) as Pourcentage_Victoires_Facile,
                    SUM(Gagne_Facile) as Victoires_Faciles
                FROM Partie
                JOIN User ON Partie.User_Id = User.US_Id
                GROUP BY Nom_Utilisateur
                ORDER BY Nom_Utilisateur DESC;
            """)
        elif sort_key == 'victoire_asc_facile':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' AND Difficulty = 'facile' THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN Difficulty = 'facile' THEN 1 ELSE 0 END), 2) as Pourcentage_Victoires_Facile,
                    SUM(Gagne_Facile) as Victoires_Faciles
                FROM Partie
                JOIN User ON Partie.User_Id = User.US_Id
                GROUP BY Nom_Utilisateur
                ORDER BY Pourcentage_Victoires_Facile DESC;
            """)
        elif sort_key == 'victoire_desc_facile':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' AND Difficulty = 'facile' THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN Difficulty = 'facile' THEN 1 ELSE 0 END), 2) as Pourcentage_Victoires_Facile,
                    SUM(Gagne_Facile) as Victoires_Faciles
                FROM Partie
                JOIN User ON Partie.User_Id = User.US_Id
                GROUP BY Nom_Utilisateur
                ORDER BY Pourcentage_Victoires_Facile ASC;
            """)
        elif sort_key == 'nombre_de_victoire_total_facile_asc_facile':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' AND Difficulty = 'facile' THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN Difficulty = 'facile' THEN 1 ELSE 0 END), 2) as Pourcentage_Victoires_Facile,
                    SUM(Gagne_Facile) as Victoires_Faciles
                FROM 
                    Partie
                JOIN 
                    User ON Partie.User_Id = User.US_Id
                GROUP BY 
                    User.Nom_Utilisateur
                ORDER BY 
                    Victoires_Faciles DESC;
            """)
        elif sort_key == 'nombre_de_victoire_total_facile_desc_facile':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' AND Difficulty = 'facile' THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN Difficulty = 'facile' THEN 1 ELSE 0 END), 2) as Pourcentage_Victoires_Facile,
                    SUM(Gagne_Facile) as Victoires_Faciles
                FROM 
                    Partie
                JOIN 
                    User ON Partie.User_Id = User.US_Id
                GROUP BY 
                    User.Nom_Utilisateur
                ORDER BY 
                    Victoires_Faciles ASC;
            """)

            #Cas ou moyen est coché
        elif sort_key == 'nom_asc_moyen':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' AND Difficulty = 'moyen' THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN Difficulty = 'moyen' THEN 1 ELSE 0 END), 2) as Pourcentage_Victoires_Moyen,
                    SUM(Gagne_Moyen) as Victoires_Moyen
                FROM Partie
                JOIN User ON Partie.User_Id = User.US_Id
                GROUP BY Nom_Utilisateur
                ORDER BY Nom_Utilisateur ASC;
            """)
        elif sort_key == 'nom_desc_moyen':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' AND Difficulty = 'moyen' THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN Difficulty = 'moyen' THEN 1 ELSE 0 END), 2) as Pourcentage_Victoires_Moyen,
                    SUM(Gagne_Moyen) as Victoires_Moyen
                FROM Partie
                JOIN User ON Partie.User_Id = User.US_Id
                GROUP BY Nom_Utilisateur
                ORDER BY Nom_Utilisateur DESC;
            """)
        elif sort_key == 'victoire_asc_moyen':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' AND Difficulty = 'moyen' THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN Difficulty = 'moyen' THEN 1 ELSE 0 END), 2) as Pourcentage_Victoires_Moyen,
                    SUM(Gagne_Moyen) as Victoires_Moyen
                FROM Partie
                JOIN User ON Partie.User_Id = User.US_Id
                GROUP BY Nom_Utilisateur
                ORDER BY Pourcentage_Victoires_Moyen DESC;
            """)
        elif sort_key == 'victoire_desc_moyen':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' AND Difficulty = 'moyen' THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN Difficulty = 'moyen' THEN 1 ELSE 0 END), 2) as Pourcentage_Victoires_Moyen,
                    SUM(Gagne_Moyen) as Victoires_Moyen
                FROM Partie
                JOIN User ON Partie.User_Id = User.US_Id
                GROUP BY Nom_Utilisateur
                ORDER BY Pourcentage_Victoires_Moyen ASC;
            """)
        elif sort_key == 'nombre_de_victoire_total_moyen_asc_moyen':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' AND Difficulty = 'moyen' THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN Difficulty = 'moyen' THEN 1 ELSE 0 END), 2) as Pourcentage_Victoires_Moyen,
                    SUM(Gagne_Moyen) as Victoires_Moyen
                FROM 
                    Partie
                JOIN 
                    User ON Partie.User_Id = User.US_Id
                GROUP BY 
                    User.Nom_Utilisateur
                ORDER BY 
                    Victoires_Moyen DESC;
            """)
        elif sort_key == 'nombre_de_victoire_total_moyen_desc_moyen':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' AND Difficulty = 'moyen' THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN Difficulty = 'moyen' THEN 1 ELSE 0 END), 2) as Pourcentage_Victoires_Moyen,
                    SUM(Gagne_Moyen) as Victoires_Moyen
                FROM 
                    Partie
                JOIN 
                    User ON Partie.User_Id = User.US_Id
                GROUP BY 
                    User.Nom_Utilisateur
                ORDER BY 
                    Victoires_Moyen ASC;
            """)

         #Cas ou difficile est coché
        elif sort_key == 'nom_asc_difficile':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' AND Difficulty = 'difficile' THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN Difficulty = 'difficile' THEN 1 ELSE 0 END), 2) as Pourcentage_Victoires_Difficile,
                    SUM(Gagne_Difficile) as Victoires_Difficile
                FROM Partie
                JOIN User ON Partie.User_Id = User.US_Id
                GROUP BY Nom_Utilisateur
                ORDER BY Nom_Utilisateur ASC;
            """)
        elif sort_key == 'nom_desc_difficile':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' AND Difficulty = 'difficile' THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN Difficulty = 'difficile' THEN 1 ELSE 0 END), 2) as Pourcentage_Victoires_Difficile,
                    SUM(Gagne_Difficile) as Victoires_Difficile
                FROM Partie
                JOIN User ON Partie.User_Id = User.US_Id
                GROUP BY Nom_Utilisateur
                ORDER BY Nom_Utilisateur DESC;
            """)
        elif sort_key == 'victoire_asc_difficile':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' AND Difficulty = 'difficile' THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN Difficulty = 'difficile' THEN 1 ELSE 0 END), 2) as Pourcentage_Victoires_Difficile,
                    SUM(Gagne_Difficile) as Victoires_Difficile
                FROM Partie
                JOIN User ON Partie.User_Id = User.US_Id
                GROUP BY Nom_Utilisateur
                ORDER BY Pourcentage_Victoires_Difficile DESC;
            """)
        elif sort_key == 'victoire_desc_difficile':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' AND Difficulty = 'difficile' THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN Difficulty = 'difficile' THEN 1 ELSE 0 END), 2) as Pourcentage_Victoires_Difficile,
                    SUM(Gagne_Difficile) as Victoires_Difficile
                FROM Partie
                JOIN User ON Partie.User_Id = User.US_Id
                GROUP BY Nom_Utilisateur
                ORDER BY Pourcentage_Victoires_Difficile ASC;
            """)
        elif sort_key == 'nombre_de_victoire_total_difficile_desc_difficile':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' AND Difficulty = 'difficile' THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN Difficulty = 'difficile' THEN 1 ELSE 0 END), 2) as Pourcentage_Victoires_Difficile,
                    SUM(Gagne_Difficile) as Victoires_Difficile
                FROM 
                    Partie
                JOIN 
                    User ON Partie.User_Id = User.US_Id
                GROUP BY 
                    User.Nom_Utilisateur
                ORDER BY 
                    Victoires_Difficile ASC;
            """)
        elif sort_key == 'nombre_de_victoire_total_difficile_asc_difficile':
            cursor.execute("""
                SELECT Nom_Utilisateur, 
                    ROUND(SUM(CASE WHEN Resultat = 'Gagné' AND Difficulty = 'difficile' THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN Difficulty = 'difficile' THEN 1 ELSE 0 END), 2) as Pourcentage_Victoires_Difficile,
                    SUM(Gagne_Difficile) as Victoires_Difficile
                FROM 
                    Partie
                JOIN 
                    User ON Partie.User_Id = User.US_Id
                GROUP BY 
                    User.Nom_Utilisateur
                ORDER BY 
                    Victoires_Difficile DESC;
            """)

        classement_data = cursor.fetchall()
    return classement_data

@app.route('/classement_total', methods=['GET', 'POST'])
def classement_total():
    sort_key = request.form.get('sort_key', 'nom_asc_total') #Par défaut
    classement_data = get_classement_data(sort_key)
    return render_template('classement_total.html', classement_data=classement_data, sort_key=sort_key)
@app.route('/classement_facile', methods=['GET', 'POST'])
def classement_facile():
    sort_key = request.form.get('sort_key', 'nom_asc_facile')
    classement_data = get_classement_data(sort_key)
    return render_template('classement_facile.html', classement_data=classement_data, sort_key=sort_key)
@app.route('/classement_moyen', methods=['GET', 'POST'])
def classement_moyen():
    sort_key = request.form.get('sort_key', 'nom_asc_moyen') 
    classement_data = get_classement_data(sort_key)
    return render_template('classement_moyen.html', classement_data=classement_data, sort_key=sort_key)
@app.route('/classement_difficile', methods=['GET', 'POST'])
def classement_difficile():
    sort_key = request.form.get('sort_key', 'nom_asc_difficile') 
    classement_data = get_classement_data(sort_key)
    return render_template('classement_difficile.html', classement_data=classement_data, sort_key=sort_key)

#Statistique + Historique de toutes les parties
@app.route('/historique')
def historique():
    user_id = session.get('user_id')
    historique_data = get_historique_data(user_id)
    return render_template('historique.html', **historique_data)
                  
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    connection.commit()
    connection.close()
