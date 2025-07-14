def get_google_scholar_publications_from_url(url, max_publications=5, max_retries=3):
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

def main():
    print("=== Iniciando atualização do README ===")
    scholar_url = os.getenv("GOOGLE_SCHOLAR_URL")

    if not scholar_url:
        print("❌ Variável de ambiente GOOGLE_SCHOLAR_URL não definida.")
        return

    print(f"🔍 Buscando publicações em: {scholar_url}")
    publications = get_google_scholar_publications_from_url(scholar_url)

    update_readme(publications)
    print("🏁 Finalizado.")

