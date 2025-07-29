import sqlite3
import os

# Connexion à la base de données SQLite
con = sqlite3.connect('plaques.sqlite')
cur = con.cursor()

# Vérifie si une plaque existe déjà dans la base
def verif(plaque):
    cur.execute("SELECT 1 FROM plaques WHERE plaque = ?", (plaque,))
    return cur.fetchone() is not None

# Met à jour ou insère une plaque avec note et commentaire
def report(plaque, note, commentaire):
    if verif(plaque):
        # Si un commentaire est fourni, on le met à jour dans le fichier existant
        if commentaire:
            with open(f"comentaire//{plaque}.txt", "a+", encoding="utf-8") as f:
                f.write(f"{commentaire}\n")

        # On récupère les valeurs existantes
        val = cur.execute("SELECT Note, NbsNotes FROM plaques WHERE plaque = ?", (plaque,)).fetchone()
        if val:
            note_moyenne, nb_notes = val
            nouvelle_note = (note + note_moyenne) / (nb_notes + 1)
            cur.execute("UPDATE plaques SET Note = ?, NbsNotes = ? WHERE plaque = ?",(nouvelle_note, nb_notes + 1, plaque))
    else:
        # Nouveau commentaire enregistré dans un nouveau fichier
        commentaire_path = f"comentaire//{plaque}.txt"
        if commentaire:
            with open(commentaire_path, "a+", encoding="utf-8") as f:
                f.write(f"{commentaire}\n")
        else:
            commentaire_path = None

        # Insertion d’une nouvelle ligne
        cur.execute("INSERT INTO plaques (plaque, Note, NbsNotes, Commentaires) VALUES (?, ?, ?, ?)",(plaque, note, 1, commentaire_path))

    con.commit()

def classement(top):
    plaques = cur.execute("SELECT Plaque, Note FROM plaques").fetchall()
    data = {plaque: score for plaque, score in plaques}
    sorted_items = sorted(data.items(), key=lambda it: it[1], reverse=True)
    top_items = sorted_items[:top]
    return dict(top_items)


