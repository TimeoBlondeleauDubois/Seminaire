import sqlite3
from bcrypt import hashpw, gensalt

connection = sqlite3.connect('ParkEase.db')
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS User (
        US_Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Nom_Utilisateur TEXT UNIQUE NOT NULL,
        Mot_De_Passe TEXT NOT NULL,
        Est_Premium INTEGER NOT NULL DEFAULT 0,
        Immatriculation TEXT NOT NULL
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Parking (
        Park_Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Nom_Parking TEXT UNIQUE NOT NULL,
        Adresse_Parking TEXT NOT NULL,
        Ville_Parking TEXT NOT NULL,
        Hauteur_max REAL NOT NULL,
        A_Places_handicapees INTEGER NOT NULL DEFAULT 0,
        Est_Sous_Surveillance INTEGER NOT NULL DEFAULT 0,
        Est_Couvert INTEGER NOT NULL DEFAULT 0
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Place (
        Place_Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Nom_Place TEXT UNIQUE NOT NULL,  
        Park_Id INTEGER NOT NULL,
        FOREIGN KEY(Park_Id) REFERENCES Parking(Park_Id) ON DELETE CASCADE       
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Reservation (
        Reservation_Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Date_Debut_Reservation TEXT NOT NULL,
        Date_Fin_Reservation TEXT NOT NULL,
        User_Id INTEGER NOT NULL,
        Place_Id INTEGER NOT NULL,
        FOREIGN KEY(User_Id) REFERENCES User(US_Id) ON DELETE CASCADE,       
        FOREIGN KEY(Place_Id) REFERENCES Place(Place_Id) ON DELETE CASCADE
    );
""")

connection.commit()
