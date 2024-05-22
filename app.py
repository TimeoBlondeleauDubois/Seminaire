from flask import Flask, render_template, request, redirect, url_for, session
from bcrypt import hashpw, gensalt
import sqlite3, random
from datetime import datetime
from flask import flash

app = Flask(__name__)
app.secret_key = 'b_5#y2L"F4Q8z\n\xec]/'

connection = sqlite3.connect('ParkEase.db')
cursor = connection.cursor()

@app.route('/')
def loginpage():
    return render_template('login.html')

def connect_db():
    db_path = 'ParkEase.db'
    return sqlite3.connect(db_path)

#Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_credentials(username, password):
            return redirect(url_for('home'))
        else:
            error = 'Nom d\'utilisateur ou mot de passe incorrect'
    return render_template('login.html', error=error)

#Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        immatriculation = request.form['immatriculation']
        print(f"Avant create_user: {username}, {password}")
        if create_user(username, password, immatriculation):
            print("Après create_user: Utilisateur créé avec succès")
            return redirect(url_for('login'))
        else:
            error = 'Nom d\'utilisateur déjà pris'
    return render_template('signup.html', error=error)

#Home
@app.route('/home')
def home():
    return render_template('home.html')

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

#Creer un utilisateur
def create_user(username, password, immatriculation):
    try:
        hashed_password = hashpw(password.encode('utf-8'), gensalt())
        with connect_db() as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO User (Nom_Utilisateur, Mot_De_Passe, immatriculation) VALUES (?, ?, ?)", (username, hashed_password, immatriculation))
        print(f"Utilisateur {username} créé avec succès")
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la création de l'utilisateur : {e}")
        return False
    
@app.route('/detailparking')
def detailparking():
    return render_template('DetailParking.html')
            
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    connection.commit()
    connection.close()
