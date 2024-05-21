import sqlite3
from bcrypt import hashpw, gensalt

connection = sqlite3.connect('ParkEase.db')
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS User (
        US_Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Nom_Utilisateur VARCHAR UNIQUE,
        Mot_De_Passe VARCHAR
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Parking (
        Park_Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Nom_Parking VARCHAR UNIQUE,
        Adresse_Parking VARCHAR,
        Ville_Parking VARCHAR  
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Places (
        Place_Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Nom_Place VARCHAR UNIQUE,
        Park_id INTEGER UNIQUE,
        FOREIGN KEY(Park_id) REFERENCES Parking(Park_Id)       
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS User_Parking (
        User_Parking_id INTEGER PRIMARY KEY,
        User_id INTEGER,
        Park_id INTEGER,
        FOREIGN KEY(Park_id) REFERENCES Parking(Park_Id),
        FOREIGN KEY(User_id) REFERENCES User(User_id)       
    );
""")


connection.commit()