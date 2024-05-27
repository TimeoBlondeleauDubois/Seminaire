from flask import Flask, render_template, request, redirect, url_for, session
from bcrypt import hashpw, gensalt
import sqlite3, random
from datetime import datetime, timedelta
from flask import flash
import os

app = Flask(__name__)
app.secret_key = os.urandom(1024)

connection = sqlite3.connect('ParkEase.db')
cursor = connection.cursor()

@app.route('/')
def loginpage():
    return render_template('login.html')

def connect_db():
    db_path = os.path.join(os.path.dirname(__file__), 'ParkEase.db')
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

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        immatriculation = request.form['immatriculation']
        print(f"Tentative de création d'utilisateur : {username}")
        if create_user(username, password, immatriculation):
            print(f"Utilisateur {username} créé avec succès")
            return redirect(url_for('login'))
        else:
            print(f"Échec de la création de l'utilisateur : {username}")
            error = 'Nom d\'utilisateur déjà pris'
    return render_template('signup.html', error=error)


#home
@app.route('/home', methods=['GET','POST'])
def home():
    if request.method == 'GET':
        with connect_db() as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM Parking")
            parkings =  cursor.fetchall()
            parking1 = random.choice(parkings)
            parkings.remove(parking1)
            parking2 = random.choice(parkings)
            parkings.remove(parking2)
            parking3 = random.choice(parkings)
            parkings.remove(parking3)

            cursor.execute("SELECT COUNT(Place.Place_Id) FROM Place LEFT JOIN Reservation ON Place.Place_Id = Reservation.Place_Id AND Reservation.Date_Fin_Reservation >= datetime('now') WHERE Place.Park_Id = ? AND Reservation.Place_Id IS NULL;", (parking1[0],))
            nombre_places_disponibles_parking1 = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(Place.Place_Id) FROM Place WHERE Park_Id = ?", (parking1[0],))
            nombre_places_totales_parking1 = cursor.fetchone()[0]
            if nombre_places_disponibles_parking1 < 25:
                color1 = 'red'
            elif nombre_places_disponibles_parking1 < 50:
                color1 = 'orange'
            else:
                color1 = 'green'

            cursor.execute("SELECT COUNT(Place.Place_Id) FROM Place LEFT JOIN Reservation ON Place.Place_Id = Reservation.Place_Id AND Reservation.Date_Fin_Reservation >= datetime('now') WHERE Place.Park_Id = ? AND Reservation.Place_Id IS NULL;", (parking2[0],))
            nombre_places_disponibles_parking2 = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(Place.Place_Id) FROM Place WHERE Park_Id = ?", (parking2[0],))
            nombre_places_totales_parking2 = cursor.fetchone()[0]
            if nombre_places_disponibles_parking2 < 25:
                color2 = 'red'
            elif nombre_places_disponibles_parking2 < 50:
                color2 = 'orange'
            else:
                color2 = 'green'

            cursor.execute("SELECT COUNT(Place.Place_Id) FROM Place LEFT JOIN Reservation ON Place.Place_Id = Reservation.Place_Id AND Reservation.Date_Fin_Reservation >= datetime('now') WHERE Place.Park_Id = ? AND Reservation.Place_Id IS NULL;", (parking3[0],))
            nombre_places_disponibles_parking3 = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(Place.Place_Id) FROM Place WHERE Park_Id = ?", (parking3[0],))
            nombre_places_totales_parking3 = cursor.fetchone()[0]
            if nombre_places_disponibles_parking3 < 25:
                color3 = 'red'
            elif nombre_places_disponibles_parking3 < 50:
                color3 = 'orange'
            else:
                color3 = 'green'

        return render_template('home.html', parking1=parking1, parking2=parking2, parking3=parking3, nombre_places_disponibles_parking1=nombre_places_disponibles_parking1, nombre_places_disponibles_parking2=nombre_places_disponibles_parking2, nombre_places_disponibles_parking3=nombre_places_disponibles_parking3, nombre_places_totales_parking1=nombre_places_totales_parking1, nombre_places_totales_parking2=nombre_places_totales_parking2, nombre_places_totales_parking3=nombre_places_totales_parking3, color1=color1, color2=color2, color3=color3)
    else:
        Parking_Name = request.form['Nom_Parking']
        with connect_db() as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM Parking WHERE Ville_Parking LIKE ?", (Parking_Name + '%',))
            Infos_parking = cursor.fetchall()
            IdS = []
            nombres_places_disponibles = []  
            nombres_places_totales = []
            for Info_Parking in Infos_parking:   
                cursor.execute("SELECT COUNT(Place.Place_Id) FROM Place LEFT JOIN Reservation ON Place.Place_Id = Reservation.Place_Id AND Reservation.Date_Fin_Reservation >= datetime('now') WHERE Place.Park_Id = ? AND Reservation.Place_Id IS NULL;", (Info_Parking[0],))
                nombre_places_disponibles_parking = cursor.fetchone()[0]
                nombres_places_disponibles.append(nombre_places_disponibles_parking)  
                cursor.execute("SELECT COUNT(Place.Place_Id) FROM Place WHERE Park_Id = ?", (Info_Parking[0],))
                nombre_places_totales_parking = cursor.fetchone()[0]
                nombres_places_totales.append(nombre_places_totales_parking)
        if Infos_parking is None:
            flash('Aucun parking trouvé')
            return render_template('home.html')
        return render_template('listerecherche.html', Infos_parking=Infos_parking, IdS=IdS, nombres_places_disponibles=nombres_places_disponibles, nombres_places_totales=nombres_places_totales)  # Passez les listes au modèle


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


def create_user(username, password, immatriculation):
    try:
        with connect_db() as db:
            cursor = db.cursor()
            cursor.execute("SELECT COUNT(*) FROM User WHERE Nom_Utilisateur = ?", (username,))
            if cursor.fetchone()[0] > 0:
                print(f"Erreur : Le nom d'utilisateur {username} est déjà pris")
                return False
            hashed_password = hashpw(password.encode('utf-8'), gensalt())
            cursor.execute("INSERT INTO User (Nom_Utilisateur, Mot_De_Passe, immatriculation) VALUES (?, ?, ?)", (username, hashed_password, immatriculation))
            print(f"Utilisateur {username} créé avec succès")
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la création de l'utilisateur : {e}")
        return False

    
@app.route('/detailparking/<int:parking_id>')
def detailparking(parking_id):
    with connect_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Parking WHERE Park_Id = ?", (parking_id,))
        parking_info = cursor.fetchone()
        cursor.execute("SELECT COUNT(Place.Place_Id) FROM Place LEFT JOIN Reservation ON Place.Place_Id = Reservation.Place_Id AND Reservation.Date_Fin_Reservation >= datetime('now') WHERE Place.Park_Id = ? AND Reservation.Place_Id IS NULL;", (parking_id,))
        nombre_places_disponibles_parking = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(Place.Place_Id) FROM Place WHERE Park_Id = ?", (parking_id,))
        nombre_places_totales_parking = cursor.fetchone()[0]
    return render_template('DetailParking.html', parking_info=parking_info , nombre_places_disponibles_parking=nombre_places_disponibles_parking, nombre_places_totales_parking=nombre_places_totales_parking)

@app.route('/reservation/<int:parking_id>', methods=['GET', 'POST'])
def reservation(parking_id):
    with connect_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT Place.Place_Id FROM Place LEFT JOIN Reservation ON Place.Place_Id = Reservation.Place_Id AND Reservation.Date_Fin_Reservation >= datetime('now') WHERE Place.Park_Id = ? AND Reservation.Place_Id IS NULL;", (parking_id,))
        IdPLaceDispoTuples = cursor.fetchone()
        if IdPLaceDispoTuples is None:
            return render_template('error.html')
        IPlaceDispo = [e for e in IdPLaceDispoTuples]
        cursor.execute("INSERT INTO Reservation (Date_Debut_Reservation, Date_Fin_Reservation, User_Id, Place_Id) VALUES (?, ?, ?, ?)", (datetime.now(), datetime.now() + timedelta(hours=3), session['user_id'], IPlaceDispo[0]))
       
    return redirect(url_for('home'))



connection.commit()
connection.close()


            
if __name__ == "__main__":
    app.run(debug=True)