const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// Utilisation de LocalAuth pour la persistance automatique de la session
const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: './wwebjs_auth' // dossier où la session est stockée
    })
});

client.on('qr', (qr) => {
    qrcode.generate(qr, { small: true });
    console.log('Scanne le QR code ci-dessus pour connecter le bot à WhatsApp (uniquement au premier lancement).');
});

client.on('ready', async () => {
    console.log('✅ Bot WhatsApp prêt.');
    const chats = await client.getChats();
    const groups = chats.filter(chat => chat.isGroup);
    groups.forEach(group => {
        console.log(`Nom: ${group.name} | ID: ${group.id._serialized}`);
    });
});

// Fonction pour envoyer le document Word dans un groupe WhatsApp
async function sendReportToGroup(groupId) {
    const filePath = path.join(__dirname, 'Daily_Meeting_Report.docx');
    if (fs.existsSync(filePath)) {
        const media = MessageMedia.fromFilePath(filePath);
        await client.sendMessage(groupId, media, { caption: "Voici le rapport daily du jour." });
        console.log('📄 Rapport envoyé au groupe:', groupId);
    } else {
        console.error('❌ Fichier Daily_Meeting_Report.docx introuvable.');
    }
}

client.on('message', message => {
    if (message.body.startsWith('#daily')) {
        const cleanMessage = message.body.replace(/\"/g, '');
        fs.writeFileSync("temp_message.txt", cleanMessage);

        exec(`venv\\Scripts\\python.exe process_message.py`, (error, stdout, stderr) => {
    if (error) {
        console.error(`❌ Erreur : ${error.message}`);
    }
    if (stderr) {
        console.error(`⚠️ stderr: ${stderr}`);
    }
    console.log(`📩 Résultat : ${stdout}`);

    // Génère le document Word après la mise à jour Excel
    exec(`venv\\Scripts\\python.exe generate_doc.py`, (error2, stdout2, stderr2) => {
        if (error2) {
            console.error(`❌ Erreur (génération docx) : ${error2.message}`);
        }
        if (stderr2) {
            console.error(`⚠️ stderr (génération docx): ${stderr2}`);
        }
        console.log(`📄 Génération Word : ${stdout2}`);

        // Envoi du rapport Word dans le groupe
        sendReportToGroup('237655911568-1628088507@g.us');
    });
});
    }
});

client.initialize();
