from guimeni import parse_rapport
import pandas as pd
from datetime import datetime
import os

with open("temp_message.txt", "r", encoding="utf-8") as f:
    msg = f.read()

# Utilise le module guimeni pour parser le rapport libre
rapport = parse_rapport(msg)

# Prépare les données pour le DataFrame
row = {
    'Nom': rapport.get('Auteur', ''),
    'Date': rapport.get('Date', datetime.now().strftime('%d/%m/%Y')),
    'Travaux de la veille': '\n'.join(rapport.get('Travaux de la veille', [])),
    'Travaux du jour': '\n'.join(
        f"{item['tache']} (Avancement : {item['avancement']})" if isinstance(item, dict) and item.get('avancement') else (item['tache'] if isinstance(item, dict) else str(item))
        for item in rapport.get('Travaux du jour', [])
    ),
    'Difficultés': '\n'.join(rapport.get('Difficultés', [])) if isinstance(rapport.get('Difficultés', []), list) else rapport.get('Difficultés', ''),
    'Taches de demain': '\n'.join(rapport.get('Taches de demain', [])) if isinstance(rapport.get('Taches de demain', []), list) else rapport.get('Taches de demain', ''),
    'Observations': rapport.get('Observations', ''),
}

fichier = "data/daily_data.xlsx"
df = pd.DataFrame([row])

if os.path.exists(fichier):
    old = pd.read_excel(fichier)
    df = pd.concat([old, df], ignore_index=True)

df.to_excel(fichier, index=False)
print("Rapport sauvegardé dans Excel.")
