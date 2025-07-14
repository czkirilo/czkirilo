import os
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_google_scholar_publications(scholar_id, max_publications=5, max_retries=3):
    url = f"https://scholar.google.com/citations?user={scholar_id}&hl=en&cstart=0&pagesize=100"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for attempt in range(max_retries):
        try:
            print(f"Tentativa {attempt + 1}/{max_retries}")
            response = requests.get(url, headers=headers, timeout=20)

            if response.status_code == 429:
                print("⚠️ Rate limit atingido. Aguardando 30s...")
                time.sleep(30)
                continue

            if "captcha" in response.text.lower():
                print("❌ CAPTCHA detectado. Acesso bloqueado.")
                return None

            soup = BeautifulSoup(response.content, 'html.parser')
            rows = soup.select('tr.gsc_a_tr')

            publications = []
            for row in rows:
                title_elem = row.find('a', class_='gsc_a_at')
                year_elem = row.find('span', class_='gsc_a_h') or row.find('span', class_='gsc_a_y')

                if not title_elem:
                    continue

                title = title_elem.get_text().strip()
                href = title_elem.get('href', '')
                link = f"https://scholar.google.com{href}" if href else '#'

                year = year_elem.get_text().strip() if year_elem else "N/A"
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
            return publications[:max_publications] if publications else None

        except Exception as e:
            print(f"Erro ao buscar publicações: {e}")
            time.sleep(5)

    print("❌ Falha após múltiplas tentativas")
    return None

def update_readme(publications):
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()

        update_date = datetime.utcnow().strftime('%Y-%m-%d')
        section_title = f"## 📚 Últimas Publicações Acadêmicas (Atualizado em: {update_date})"
        section_intro = "* Este tópico é atualizado automaticamente com base nas publicações indexadas no Google Scholar via GitHub Actions*\n"

        if publications:
            pub_lines = ""
            for pub in publications:
                title = pub["title"]
                if len(title) > 100:
                    title = title[:97] + "..."
                pub_lines += f"> 📘 **{title}**\n"
                pub_lines += f"> 🗓️ {pub['year']} · 🔗 [Link]({pub['link']})\n\n"
        else:
            pub_lines = "> ⚠️ **Erro ao buscar publicações no momento**\n\n"

        new_block = f"{section_title}\n{section_intro}\n{pub_lines}".strip()

        content = re.sub(
            r"## 📚 Últimas Publicações Acadêmicas.*?(?=\n##|\Z)",
            new_block,
            content,
            flags=re.DOTALL
        )

        with open("README.md", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ README.md atualizado com sucesso!")

    except Exception as e:
        print(f"Erro ao atualizar README: {e}")

def main():
    print("=== Iniciando atualização do README ===")
    scholar_id = os.getenv("GOOGLE_SCHOLAR_ID")

    if not scholar_id:
        print("❌ Variável de ambiente GOOGLE_SCHOLAR_ID não definida.")
        return

    print(f"🔍 Buscando publicações para ID: {scholar_id}")
    publications = get_google_scholar_publications(scholar_id)

    update_readme(publications)
    print("🏁 Finalizado.")

if __name__ == "__main__":
    main()

