import re
from datetime import datetime


def parse_rapport(text):
    # Normalisation du texte (remplacement des caractères spéciaux d'espacement)
    text = re.sub(r'[\xa0\u200b]', ' ', text)

    # Extraction de la date
    date_match = re.search(r'Date\s*:\s*(.+)', text, re.IGNORECASE)
    date = date_match.group(1).strip() if date_match else datetime.now().strftime('%d/%m/%Y')

    # Extraction de l'auteur
    auteur_match = re.search(r'Auteur\s*:\s*(.+)', text, re.IGNORECASE)
    auteur = auteur_match.group(1).strip() if auteur_match else 'Inconnu'

    # Extraction des sections principales
    sections = re.split(r'^[IVX]+\.\s+', text, flags=re.MULTILINE | re.IGNORECASE)
    section_titles = re.findall(r'^[IVX]+\.\s+([^\n]+)', text, flags=re.MULTILINE | re.IGNORECASE)

    # Création d'un dictionnaire des sections (en minuscules pour faciliter la recherche)
    section_map = {}
    for title, content in zip(section_titles, sections[1:]):
        normalized_title = title.strip().lower()
        section_map[normalized_title] = content.strip()

    def extract_list_items(section_content):
        items = []
        if not section_content:
            return items

        # Détection des items numérotés ou à puces
        lines = [line.strip() for line in section_content.split('\n') if line.strip()]
        for line in lines:
            if re.match(r'^(\d+\.\s*|[-*]\s*)', line):
                items.append(re.sub(r'^\d+\.\s*|^[-*]\s*', '', line))
        return items

    def extract_travaux_jour(section_content):
        travaux = []
        if not section_content:
            return travaux

        current_task = None
        for line in section_content.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Détection d'une nouvelle tâche
            if re.match(r'^\d+\.', line):
                if current_task:
                    travaux.append(current_task)
                task_text = re.sub(r'^\d+\.\s*', '', line)
                current_task = {'tache': task_text, 'avancement': ''}
            # Détection de l'avancement
            elif current_task and line.lower().startswith('avancement'):
                current_task['avancement'] = re.sub(r'avancement\s*:\s*', '', line, flags=re.IGNORECASE).strip()

        if current_task:
            travaux.append(current_task)
        return travaux

    # Extraction des différentes sections
    travaux_veille = extract_list_items(section_map.get('travaux de la veille', ''))
    travaux_jour = extract_travaux_jour(section_map.get('travaux du jour', ''))

    # Gestion des différentes orthographes possibles pour les sections
    difficultes = extract_list_items(
        section_map.get('difficultes', '') or
        section_map.get('difficultés', '')
    )

    taches_demain = extract_list_items(
        section_map.get('taches de demain', '') or
        section_map.get('tâches de demain', '')
    )

    return {
        'Date': date,
        'Auteur': auteur,
        'Travaux de la veille': travaux_veille,
        'Travaux du jour': travaux_jour,
        'Difficultés': difficultes,
        'Taches de demain': taches_demain
    }