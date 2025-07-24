from guimeni import parse_rapport
import pandas as pd
from datetime import datetime
import os
import sys


def process_message():
    try:
        # Lire le message
        with open("temp_message.txt", "r", encoding="utf-8") as f:
            msg = f.read()

        # Parser le rapport
        rapport = parse_rapport(msg)

        # Créer le dossier data s'il n'existe pas
        os.makedirs('data', exist_ok=True)

        # Chemin du fichier Excel
        fichier = os.path.join('data', 'daily_data.xlsx')

        # Préparer les données
        new_data = {
            'Nom': [rapport.get('Auteur', '')],
            'Date': [rapport.get('Date', datetime.now().strftime('%d/%m/%Y %H:%M'))],
            'Travaux de la veille': ['\n'.join(rapport.get('Travaux de la veille', []))],
            'Travaux du jour': ['\n'.join(
                f"{item['tache']} (Avancement : {item['avancement']}%)"
                if isinstance(item, dict) and item.get('avancement')
                else (item['tache'] if isinstance(item, dict) else str(item))
                for item in rapport.get('Travaux du jour', [])
            )],
            'Difficultés': ['\n'.join(rapport.get('Difficultés', []))],
            'Taches de demain': ['\n'.join(rapport.get('Taches de demain', []))]
        }

        # Créer un nouveau DataFrame
        df_new = pd.DataFrame(new_data)

        # Si le fichier existe déjà, lire les données existantes
        if os.path.exists(fichier):
            try:
                df_old = pd.read_excel(fichier)
                # Supprimer les entrées existantes pour le même auteur
                df_old = df_old[df_old['Nom'] != new_data['Nom'][0]]
                # Concaténer les anciennes entrées avec la nouvelle
                df = pd.concat([df_old, df_new], ignore_index=True)
            except Exception as e:
                print(f"Erreur lecture ancien fichier: {e}")
                df = df_new
        else:
            df = df_new

        # Sauvegarder dans le fichier Excel
        df.to_excel(fichier, index=False)
        print("Rapport mis à jour avec succès")
        return True

    except Exception as e:
        print(f"Erreur: {str(e)}")
        return False


if __name__ == "__main__":
    if process_message():
        sys.exit(0)
    else:
        sys.exit(1)