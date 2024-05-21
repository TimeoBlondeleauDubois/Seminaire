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

connection.commit()