const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuration du client WhatsApp
const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: './wwebjs_auth'
    }),
    puppeteer: {
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

// Afficher le QR Code pour la connexion
client.on('qr', (qr) => {
    qrcode.generate(qr, { small: true });
    console.log('Scannez le QR Code avec votre téléphone pour vous connecter');
});

// Quand la connexion est établie
client.on('ready', () => {
    console.log('✅ Bot WhatsApp prêt !');
});

// Traitement des messages
client.on('message', async (message) => {
    try {
        // Vérifier si le message commence par #daily
        if (message.body.startsWith('#daily')) {
            const sender = await message.getContact();
            const senderName = sender.pushname || sender.number;
            console.log(`Nouveau rapport reçu de ${senderName}`);

            // Sauvegarder le message temporairement
            fs.writeFileSync('temp_message.txt', message.body);

            // Traiter le message
            exec('python process_message.py', (error, stdout, stderr) => {
                if (error) {
                    console.error(`Erreur: ${error.message}`);
                    return;
                }
                if (stderr) {
                    console.error(`Erreur: ${stderr}`);
                    return;
                }

                console.log('Traitement du message réussi, génération du rapport...');

                // Générer le document Word
                exec('python generate_doc.py', (error, stdout, stderr) => {
                    if (error) {
                        console.error(`Erreur génération doc: ${error.message}`);
                        return;
                    }

                    console.log('Rapport généré avec succès !');

                    // Envoyer le rapport dans le groupe
                    const docPath = path.join(__dirname, 'Daily_Meeting_Report.docx');
                    if (fs.existsSync(docPath)) {
                        const media = MessageMedia.fromFilePath(docPath);
                        message.reply(media, null, {
                            caption: '📊 Voici le rapport quotidien mis à jour !'
                        });
                    }
                });
            });
        }
    } catch (error) {
        console.error('Erreur lors du traitement du message:', error);
    }
});

// Gestion des erreurs
process.on('unhandledRejection', (reason, promise) => {
    console.error('Erreur non gérée:', reason);
});

// Démarrer le client
client.initialize();