from guimeni import parse_rapport
import pandas as pd
from datetime import datetime
import os
import sys
import traceback
import unicodedata


def normalize_text(text):
    """Normalise le texte en supprimant les caractères spéciaux problématiques"""
    if not isinstance(text, str):
        return text
    # Remplacer les apostrophes et guillemets courbés par des droits
    text = text.replace('’', "'").replace('‘', "'").replace('"', "'")
    # Normaliser les caractères Unicode
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')


def log_message(message):
    """Fonction utilitaire pour logger les messages de manière visible"""
    safe_message = normalize_text(str(message))
    print(f"=== {safe_message} ===", file=sys.stderr)
    print(safe_message, file=sys.stdout)


def ensure_data_dir():
    """Crée le répertoire data s'il n'existe pas"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(script_dir, 'data')
        log_message(f"Vérification du dossier: {data_dir}")

        if not os.path.exists(data_dir):
            log_message(f"Création du dossier: {data_dir}")
            os.makedirs(data_dir, exist_ok=True)

        if not os.path.isdir(data_dir):
            raise NotADirectoryError(f"Le chemin {data_dir} n'est pas un dossier")

        log_message(f"Dossier vérifié: {os.path.abspath(data_dir)}")
        return data_dir
    except Exception as e:
        log_message(f"ERREUR lors de la création du dossier: {str(e)}")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


def process_message():
    try:
        log_message("Début du traitement du message")
        data_dir = ensure_data_dir()
        fichier = os.path.join(data_dir, 'daily_data.xlsx')
        log_message(f"Fichier de destination: {os.path.abspath(fichier)}")

        # Lire le message avec l'encodage UTF-8
        try:
            with open("temp_message.txt", "r", encoding="utf-8") as f:
                msg = f.read()
            log_message("Message lu avec succès")
        except Exception as e:
            log_message(f"ERREUR lecture du fichier temp_message.txt: {str(e)}")
            raise

        # Parser le rapport
        try:
            log_message("Début du parsing du rapport")
            rapport = parse_rapport(msg)
            auteur = rapport.get('Auteur', 'Inconnu')
            log_message(f"Rapport parsé - Auteur: {auteur}")

            # Normaliser les données
            travaux_veille = [normalize_text(t) for t in rapport.get('Travaux de la veille', [])]
            travaux_jour = []
            for item in rapport.get('Travaux du jour', []):
                if isinstance(item, dict):
                    tache = normalize_text(item.get('tache', ''))
                    avancement = item.get('avancement', '')
                    travaux_jour.append(f"{tache} (Avancement: {avancement}%)" if avancement else tache)
                else:
                    travaux_jour.append(normalize_text(str(item)))

            difficultes = [normalize_text(d) for d in rapport.get('Difficultés', [])]
            taches_demain = [normalize_text(t) for t in rapport.get('Taches de demain', [])]

            # Préparer les données
            new_data = {
                'Nom': [normalize_text(auteur)],
                'Date': [rapport.get('Date', datetime.now().strftime('%d/%m/%Y %H:%M'))],
                'Travaux de la veille': ['\n'.join(travaux_veille)],
                'Travaux du jour': ['\n'.join(travaux_jour)],
                'Difficultés': ['\n'.join(difficultes)],
                'Taches de demain': ['\n'.join(taches_demain)]
            }

            # Créer un nouveau DataFrame
            df_new = pd.DataFrame(new_data)
            log_message("Nouveau DataFrame créé")

            # Si le fichier existe déjà, lire les données existantes
            if os.path.exists(fichier):
                try:
                    log_message("Lecture du fichier Excel existant")
                    df_old = pd.read_excel(fichier, engine='openpyxl')
                    log_message(f"Anciennes données chargées: {len(df_old)} entrées")

                    # Supprimer les entrées existantes pour le même auteur
                    df_old = df_old[df_old['Nom'] != normalize_text(auteur)]
                    log_message(f"Données après suppression: {len(df_old)} entrées")

                    # Concaténer les données
                    df = pd.concat([df_old, df_new], ignore_index=True)
                except Exception as e:
                    log_message(f"Erreur lecture ancien fichier, création nouveau: {str(e)}")
                    df = df_new
            else:
                log_message("Création d'un nouveau fichier Excel")
                df = df_new

            # Sauvegarder avec openpyxl pour un meilleur support Unicode
            log_message("Sauvegarde dans le fichier Excel...")
            with pd.ExcelWriter(fichier, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            log_message("Fichier Excel sauvegardé avec succès")
            return True

        except Exception as e:
            log_message(f"ERREUR lors du traitement du rapport: {str(e)}")
            raise

    except Exception as e:
        log_message(f"ERREUR CRITIQUE: {str(e)}")
        traceback.print_exc(file=sys.stderr)
        return False


if __name__ == "__main__":
    try:
        if process_message():
            log_message(" Traitement terminé avec succès")
            sys.exit(0)
        else:
            log_message(" Erreur lors du traitement")
            sys.exit(1)
    except Exception as e:
        log_message(f" ERREUR CRITIQUE: {str(e)}")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)