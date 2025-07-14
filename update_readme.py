import os
import re
from datetime import datetime
import time
import json

# Versão alternativa usando requests com parsing mais robusto
def get_google_scholar_publications_alternative(scholar_id):
    """
    Método alternativo para buscar publicações do Google Scholar
    """
    import requests
    from bs4 import BeautifulSoup
    
    try:
        # URL com parâmetros para mostrar mais publicações
        url = f"https://scholar.google.com/citations?user={scholar_id}&hl=en&cstart=0&pagesize=100"
        
        # Headers simulando um navegador real
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        # Fazer requisição com session
        session = requests.Session()
        session.headers.update(headers)
        
        # Primeiro, tentar acessar a página inicial do Google Scholar
        print("Acessando página inicial do Google Scholar...")
        init_response = session.get("https://scholar.google.com", timeout=10)
        time.sleep(2)
        
        # Agora acessar o perfil
        print(f"Acessando perfil: {url}")
        response = session.get(url, timeout=30)
        
        if response.status_code == 200:
            print("Página carregada com sucesso!")
            
            # Salvar HTML para debug (opcional)
            with open('debug_scholar.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Verificar se estamos bloqueados
            if "blocked" in response.text.lower() or "captcha" in response.text.lower():
                print("Bloqueado pelo Google Scholar")
                return None
            
            # Buscar publicações usando diferentes seletores
            publications = []
            
            # Método 1: Tabela padrão
            rows = soup.select('tr.gsc_a_tr')
            print(f"Método 1 - Encontradas {len(rows)} publicações")
            
            if not rows:
                # Método 2: Buscar por classe alternativa
                rows = soup.find_all('tr', {'class': 'gsc_a_tr'})
                print(f"Método 2 - Encontradas {len(rows)} publicações")
            
            if not rows:
                # Método 3: Buscar qualquer tr com link de publicação
                rows = soup.find_all('tr')
                rows = [row for row in rows if row.find('a', class_='gsc_a_at')]
                print(f"Método 3 - Encontradas {len(rows)} publicações")
            
            for i, row in enumerate(rows):
                try:
                    # Título
                    title_link = row.find('a', class_='gsc_a_at')
                    if not title_link:
                        continue
                    
                    title = title_link.get_text().strip()
                    href = title_link.get('href', '')
                    full_link = f"https://scholar.google.com{href}" if href else "#"
                    
                    # Ano - múltiplas tentativas
                    year = "N/A"
                    year_elem = row.find('span', class_='gsc_a_h')
                    if year_elem:
                        year = year_elem.get_text().strip()
                    else:
                        # Tentar encontrar ano em qualquer span
                        spans = row.find_all('span')
                        for span in spans:
                            text = span.get_text().strip()
                            if text.isdigit() and len(text) == 4 and 1900 <= int(text) <= 2030:
                                year = text
                                break
                    
                    # Validar ano
                    try:
                        year_int = int(year) if year != "N/A" else 0
                    except ValueError:
                        year_int = 0
                        year = "N/A"
                    
                    publications.append({
                        'title': title,
                        'year': year,
                        'year_int': year_int,
                        'link': full_link
                    })
                    
                    print(f"  {i+1}. {title[:60]}... ({year})")
                    
                except Exception as e:
                    print(f"Erro ao processar publicação {i+1}: {e}")
                    continue
            
            # Ordenar por ano
            publications.sort(key=lambda x: x['year_int'], reverse=True)
            
            return publications if publications else None
            
        else:
            print(f"Erro HTTP: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Erro na busca alternativa: {e}")
        return None

def update_readme_with_fallback(publications):
    """
    Atualiza o README com informações mais detalhadas sobre o erro
    """
    try:
        # Ler o README atual
        with open('README.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Seção de publicações
        if publications:
            publications_section = "**🧪 Recent Publications**\n"
            publications_section += "*This section is updated automatically with my latest publications from Google Scholar*\n\n"
            
            for pub in publications:
                # Limitar título se for muito longo
                title = pub['title']
                if len(title) > 100:
                    title = title[:97] + "..."
                
                publications_section += f"> 📘 **{title}**\n"
                publications_section += f"> 🗓️ {pub['year']} · 🔗 [Link]({pub['link']})\n\n"
        else:
            publications_section = "**🧪 Recent Publications**\n"
            publications_section += "*This section is updated automatically with my latest publications from Google Scholar*\n\n"
            publications_section += "> ⚠️ **Error fetching publications**\n"
            publications_section += f"> Unable to retrieve publications from Google Scholar at this time.\n"
            publications_section += f"> Last attempt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
        
        # Encontrar e substituir a seção existente
        pattern = r'(\*\*🧪 Recent Publications\*\*.*?)(?=\n\*\*[^*]|\n##|\n#|\Z)'
        
        if re.search(pattern, content, re.DOTALL):
            # Substituir seção existente
            new_content = re.sub(pattern, publications_section.rstrip(), content, flags=re.DOTALL)
        else:
            # Adicionar no final se não existir
            new_content = content.rstrip() + '\n\n' + publications_section
        
        # Escrever o arquivo atualizado
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("README.md atualizado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao atualizar README: {e}")

def main():
    print("=== Google Scholar Publications Updater ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Verificar se o arquivo README existe
    if not os.path.exists('README.md'):
        print("ERRO: Arquivo README.md não encontrado!")
        return
    
    # Obter o ID do Google Scholar
    scholar_id = os.getenv('GOOGLE_SCHOLAR_ID')
    
    if not scholar_id:
        print("ERRO: GOOGLE_SCHOLAR_ID não definido!")
        return
    
    print(f"Google Scholar ID: {scholar_id}")
    
    # Primeira tentativa com método principal
    print("\n=== Tentativa 1: Método Principal ===")
    publications = get_google_scholar_publications_alternative(scholar_id)
    
    if publications:
        print(f"✅ Sucesso! Encontradas {len(publications)} publicações")
    else:
        print("❌ Método principal falhou")
    
    # Atualizar README
    update_readme_with_fallback(publications)
    
    print("\n=== Processo concluído ===")

if __name__ == "__main__":
    main()
