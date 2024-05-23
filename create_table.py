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
        Est_Couvert INTEGER NOT NULL DEFAULT 0,
        Est_Horaire_24h INTEGER NOT NULL DEFAULT 0 
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Place (
        Place_Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Nom_Place TEXT NOT NULL,  
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

cursor.execute("INSERT INTO Parking (Nom_Parking, Adresse_Parking, Ville_Parking, Hauteur_max, A_Places_handicapees, Est_Sous_Surveillance, Est_Couvert, Est_Horaire_24h) VALUES ('Rouen', '1 Rue de la République, Rouen', 'Rouen', 2.0, 1, 1, 1, 0);")
cursor.execute("INSERT INTO Parking (Nom_Parking, Adresse_Parking, Ville_Parking, Hauteur_max, A_Places_handicapees, Est_Sous_Surveillance, Est_Couvert, Est_Horaire_24h) VALUES ('Rouen centre ville', '2 Avenue de Normandie, Rouen', 'Rouen', 2.5, 1, 0, 1, 1);")
cursor.execute("INSERT INTO Parking (Nom_Parking, Adresse_Parking, Ville_Parking, Hauteur_max, A_Places_handicapees, Est_Sous_Surveillance, Est_Couvert, Est_Horaire_24h) VALUES ('Paris', '10 Boulevard Montmartre, Paris', 'Paris', 2.0, 0, 1, 1 , 0);")
cursor.execute("INSERT INTO Parking (Nom_Parking, Adresse_Parking, Ville_Parking, Hauteur_max, A_Places_handicapees, Est_Sous_Surveillance, Est_Couvert, Est_Horaire_24h) VALUES ('Lyon', '5 Place Bellecour, Lyon', 'Lyon', 2.5, 1, 1, 0, 1);")
cursor.execute("INSERT INTO Parking (Nom_Parking, Adresse_Parking, Ville_Parking, Hauteur_max, A_Places_handicapees, Est_Sous_Surveillance, Est_Couvert, Est_Horaire_24h) VALUES ('Marseille', '15 Quai des Belges, Marseille', 'Marseille', 2.2, 0, 0, 1, 0);")


cursor.execute("INSERT INTO Place (Nom_Place, Park_Id) VALUES ('A1', 1);")
cursor.execute("INSERT INTO Place (Nom_Place, Park_Id) VALUES ('A2', 1);")
cursor.execute("INSERT INTO Place (Nom_Place, Park_Id) VALUES ('A3', 1);")

cursor.execute("INSERT INTO Place (Nom_Place, Park_Id) VALUES ('b1', 2);")
cursor.execute("INSERT INTO Place (Nom_Place, Park_Id) VALUES ('b2', 2);")
cursor.execute("INSERT INTO Place (Nom_Place, Park_Id) VALUES ('b3', 2);")
cursor.execute("INSERT INTO Place (Nom_Place, Park_Id) VALUES ('b4', 2);")
cursor.execute("INSERT INTO Place (Nom_Place, Park_Id) VALUES ('b5', 2);")

cursor.execute("INSERT INTO Place (Nom_Place, Park_Id) VALUES ('C1', 3);")
cursor.execute("INSERT INTO Place (Nom_Place, Park_Id) VALUES ('C2', 3);")
cursor.execute("INSERT INTO Place (Nom_Place, Park_Id) VALUES ('C3', 3);")
cursor.execute("INSERT INTO Place (Nom_Place, Park_Id) VALUES ('C4', 3);")
cursor.execute("INSERT INTO Place (Nom_Place, Park_Id) VALUES ('C5', 3);")

cursor.execute("INSERT INTO Place (Nom_Place, Park_Id) VALUES ('D1', 4);")
cursor.execute("INSERT INTO Place (Nom_Place, Park_Id) VALUES ('D2', 4);")
cursor.execute("INSERT INTO Place (Nom_Place, Park_Id) VALUES ('D3', 4);")
cursor.execute("INSERT INTO Place (Nom_Place, Park_Id) VALUES ('D4', 4);")
cursor.execute("INSERT INTO Place (Nom_Place, Park_Id) VALUES ('D5', 4);")

cursor.execute("INSERT INTO Place (Nom_Place, Park_Id) VALUES ('E1', 5);")
cursor.execute("INSERT INTO Place (Nom_Place, Park_Id) VALUES ('E2', 5);")
cursor.execute("INSERT INTO Place (Nom_Place, Park_Id) VALUES ('E3', 5);")
cursor.execute("INSERT INTO Place (Nom_Place, Park_Id) VALUES ('E4', 5);")

cursor.execute("INSERT INTO Reservation (Date_Debut_Reservation, Date_Fin_Reservation, User_Id, Place_Id) VALUES ('2024-05-25 08:00', '2024-06-25 18:00', 1, 1);")
cursor.execute("INSERT INTO Reservation (Date_Debut_Reservation, Date_Fin_Reservation, User_Id, Place_Id) VALUES ('2024-05-26 09:00', '2024-06-26 17:00', 2, 2);")
cursor.execute("INSERT INTO Reservation (Date_Debut_Reservation, Date_Fin_Reservation, User_Id, Place_Id) VALUES ('2024-04-26 09:00', '2024-04-26 17:00', 2, 16);")
cursor.execute("INSERT INTO Reservation (Date_Debut_Reservation, Date_Fin_Reservation, User_Id, Place_Id) VALUES ('2024-04-26 09:00', '2025-04-26 17:00', 2, 16);")

connection.commit()
