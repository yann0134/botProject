@echo off
REM Active l’environnement virtuel Python
call venv\Scripts\activate

REM Lance le bot WhatsApp (Node.js)
node index.js

REM (Optionnel) Désactive l’environnement virtuel à la fermeture
deactivate

pause