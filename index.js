const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// ID du groupe WhatsApp où envoyer le rapport
const TARGET_GROUP_ID = "237655911568-1628088507@g.us"; // Remplacez par l'ID de votre groupe

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
    console.log(`Le rapport sera envoyé au groupe avec l'ID: ${TARGET_GROUP_ID}`);
});

// Fonction pour envoyer le document au groupe
async function sendReportToGroup() {
    try {
        const docPath = path.join(__dirname, 'Daily_Meeting_Report.docx');
        if (fs.existsSync(docPath)) {
            const media = MessageMedia.fromFilePath(docPath);
            const groupChat = await client.getChatById(TARGET_GROUP_ID);
            await groupChat.sendMessage(media, {
                caption: '📊 Rapport quotidien mis à jour !'
            });
            console.log('Rapport envoyé avec succès au groupe');
        } else {
            console.error('Le fichier du rapport est introuvable');
        }
    } catch (error) {
        console.error('Erreur lors de l\'envoi au groupe:', error);
    }
}

// Traitement des messages
/*client.on('message', async (message) => {
    try {
        // Vérifier si le message commence par #daily
        if (message.body.startsWith('#daily')) {
            const sender = await message.getContact();
            console.log(`Nouveau rapport reçu de ${sender.pushname || sender.number}`);

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

                    // Envoyer le rapport au groupe
                    sendReportToGroup();
                });
            });
        }
    } catch (error) {
        console.error('Erreur lors du traitement du message:', error);
    }
});*/
client.on('message', async (message) => {
    try {
        if (message.body.startsWith('#daily')) {
            const sender = await message.getContact();
            console.log(`Nouveau rapport reçu de ${sender.pushname || sender.number}`);

            // Sauvegarder le message temporairement
            fs.writeFileSync('temp_message.txt', message.body);
            console.log('Message sauvegardé dans temp_message.txt');

            // Exécuter avec un timeout plus long et capturer toute la sortie
            exec('python process_message.py', {
                timeout: 30000, // 30 secondes de timeout
                maxBuffer: 1024 * 1024 * 5 // 5MB de buffer
            }, (error, stdout, stderr) => {
                console.log('=== Sortie de process_message.py ===');
                if (stdout) console.log(stdout);
                if (stderr) {
                    console.error('=== Erreurs ===');
                    console.error(stderr);
                }

                if (error) {
                    console.error('=== Détails de l\'erreur ===');
                    console.error('Code:', error.code);
                    console.error('Signal:', error.signal);
                    console.error('Sortie complète:', error);
                    return;
                }

                console.log('Traitement du message réussi, génération du rapport...');

                // Générer le document Word
                exec('python generate_doc.py', {
                    timeout: 30000,
                    maxBuffer: 1024 * 1024 * 5
                }, (error, stdout, stderr) => {
                    console.log('=== Sortie de generate_doc.py ===');
                    if (stdout) console.log(stdout);
                    if (stderr) console.error('Erreurs:', stderr);

                    if (error) {
                        console.error('Erreur lors de la génération du document:');
                        console.error(error);
                        return;
                    }

                    console.log('Rapport généré avec succès !');
                    sendReportToGroup();
                });
            });
        }
    } catch (error) {
        console.error('Erreur dans le gestionnaire de message:', error);
    }
});


// Gestion des erreurs
process.on('unhandledRejection', (reason, promise) => {
    console.error('Erreur non gérée:', reason);
});

// Démarrer le client
client.initialize();