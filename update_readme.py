# update_readme.py AGORA VAI
import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_publications(scholar_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(scholar_url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"Erro ao acessar o Google Scholar: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.select('tr.gsc_a_tr')

        publications = []
        for row in rows:
            title_elem = row.find('a', class_='gsc_a_at')
            year_elem = row.find('span', class_='gsc_a_h') or row.find('span', class_='gsc_a_y')

            if not title_elem:
                continue

            title = title_elem.get_text(strip=True)
            href = title_elem.get('href', '')
            link = f"https://scholar.google.com{href}" if href else '#'
            year = year_elem.get_text(strip=True) if year_elem else 'N/A'

            try:
                year_int = int(year)
            except:
                year_int = 0

            publications.append({
                'title': title,
                'year': year,
                'year_int': year_int,
                'link': link
            })

        publications.sort(key=lambda x: x['year_int'], reverse=True)
        return publications[:5]  # apenas 5 mais recentes

    except Exception as e:
        print(f"Erro geral: {e}")
        return []

def update_readme(publications):
    if not os.path.exists('README.md'):
        print("Arquivo README.md não encontrado.")
        return

    with open('README.md', 'r', encoding='utf-8') as f:
        readme = f.read()

    section_pattern = r'(## \ud83d\udcda \u00daltimas Publica\u00e7\u00f5es Acad\u00eamicas)(.*?)((\n##|\n#|\Z))'
    match = re.search(section_pattern, readme, flags=re.DOTALL)

    if not match:
        print("Seção de publicações não encontrada no README.md")
        return

    now = datetime.now().strftime('%Y-%m-%d')
    new_section = f"## \ud83d\udcda \u00daltimas Publica\u00e7\u00f5es Acad\u00eamicas ({now})\n"
    new_section += "*Atualizado automaticamente a partir do Google Scholar.*\n\n"

    for pub in publications:
        new_section += f"> \ud83d\udcd8 **{pub['title']}**\n"
        new_section += f"> \ud83d\uddd3️ {pub['year']} · \ud83d\udd17 [Link]({pub['link']})\n\n"

    updated_readme = re.sub(section_pattern, new_section + r"\3", readme, flags=re.DOTALL)

    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(updated_readme)

    print("README.md atualizado com sucesso.")

def main():
    scholar_url = os.getenv("GOOGLE_SCHOLAR_URL")
    if not scholar_url:
        print("Variável de ambiente GOOGLE_SCHOLAR_URL não encontrada.")
        return

    publications = get_publications(scholar_url)
    update_readme(publications)

if __name__ == '__main__':
    main()
