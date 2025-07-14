import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

def get_google_scholar_publications(scholar_id):
    """
    Busca publicações do Google Scholar
    """
    try:
        # URL do perfil do Google Scholar
        url = f"https://scholar.google.com/citations?user={scholar_id}&hl=en&oi=ao"
        
        # Headers para simular um navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fazer a requisição
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse do HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        publications = []
        
        # Encontrar todas as publicações
        pub_rows = soup.find_all('tr', class_='gsc_a_tr')
        
        for row in pub_rows:
            try:
                # Título e link
                title_elem = row.find('a', class_='gsc_a_at')
                if not title_elem:
                    continue
                    
                title = title_elem.get_text().strip()
                link = "https://scholar.google.com" + title_elem.get('href', '')
                
                # Ano
                year_elem = row.find('span', class_='gsc_a_h')
                year = year_elem.get_text().strip() if year_elem else 'N/A'
                
                # Validar se o ano é um número válido
                try:
                    year_int = int(year) if year != 'N/A' else 0
                except ValueError:
                    year_int = 0
                
                publications.append({
                    'title': title,
                    'year': year,
                    'year_int': year_int,
                    'link': link
                })
                
            except Exception as e:
                print(f"Erro ao processar publicação: {e}")
                continue
        
        # Ordenar por ano decrescente
        publications.sort(key=lambda x: x['year_int'], reverse=True)
        
        return publications
        
    except requests.RequestException as e:
        print(f"Erro de requisição: {e}")
        return None
    except Exception as e:
        print(f"Erro geral: {e}")
        return None

def update_readme(publications):
    """
    Atualiza o README.md com as publicações
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
                publications_section += f"> 📘 **{pub['title']}**\n"
                publications_section += f"> 🗓️ {pub['year']} · 🔗 [Link]({pub['link']})\n\n"
        else:
            publications_section = "**🧪 Recent Publications**\n"
            publications_section += "*This section is updated automatically with my latest publications from Google Scholar*\n\n"
            publications_section += "> ⚠️ **Error fetching publications**\n"
            publications_section += "> Unable to retrieve publications from Google Scholar at this time.\n\n"
        
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
    print("=== Iniciando atualização do README ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Verificar se o arquivo README existe
    if not os.path.exists('README.md'):
        print("ERRO: Arquivo README.md não encontrado!")
        return
    
    # Obter o ID do Google Scholar das variáveis de ambiente
    scholar_id = os.getenv('GOOGLE_SCHOLAR_ID')
    
    if not scholar_id:
        print("ERRO: GOOGLE_SCHOLAR_ID não definido!")
        print("Certifique-se de definir o secret GOOGLE_SCHOLAR_ID no GitHub")
        return
    
    print(f"✅ GOOGLE_SCHOLAR_ID encontrado: {scholar_id}")
    print(f"🔍 Buscando publicações para o ID: {scholar_id}")
    
    # Buscar publicações
    publications = get_google_scholar_publications(scholar_id)
    
    if publications is not None:
        print(f"✅ Encontradas {len(publications)} publicações")
        
        # Mostrar as primeiras publicações para debug
        for i, pub in enumerate(publications[:3]):
            print(f"  {i+1}. {pub['title']} ({pub['year']})")
        
        if len(publications) > 3:
            print(f"  ... e mais {len(publications) - 3} publicações")
    else:
        print("❌ Falha ao buscar publicações")
    
    print("📝 Atualizando README.md...")
    
    # Atualizar README
    update_readme(publications)
    
    print("=== Processo concluído ===")

if __name__ == "__main__":
    main()
