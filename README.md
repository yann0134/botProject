# Bot Daily Meeting WhatsApp

## Fonctionnalités
- Réception automatique des rapports via WhatsApp (`#daily`)
- Stockage dans Excel
- Génération automatique d'un document Word
- Envoi du rapport dans un groupe WhatsApp

## Prérequis
- Node.js + whatsapp-web.js
- Python 3 + packages : pandas, python-docx, pywhatkit

## Installation
## Installation dans un environnement virtuel Python

1. Crée un environnement virtuel :
   
   ```bash
   python -m venv venv
   ```
2. Active-le :
   - Windows :
     ```bash
     .\\venv\\Scripts\\activate
     ```
   - Mac/Linux :
     ```bash
     source venv/bin/activate
     ```
3. Installe les dépendances Python :
   ```bash
   pip install -r requirements.txt
   ```

## Installation Node.js
npm install whatsapp-web.js

## Démarrer le bot
node index.js

## Générer et envoyer manuellement
python generate_doc.py
python send_report.py
