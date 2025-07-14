import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

def get_google_scholar_publications(scholar_id):
    """
    Busca publicações do Google Scholar com múltiplas tentativas
    """
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            print(f"Tentativa {attempt + 1}/{max_retries}")
            
            # URL do perfil do Google Scholar
            url = f"https://scholar.google.com/citations?user={scholar_id}&hl=en&oi=ao"
            print(f"URL: {url}")
            
            # Headers mais robustos para simular um navegador real
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
            }
            
            # Criar sessão para manter cookies
            session = requests.Session()
            session.headers.update(headers)
            
            # Fazer a requisição com timeout
            response = session.get(url, timeout=30)
            print(f"Status Code: {response.status_code}")
            
            # Verificar se a resposta é válida
            if response.status_code == 429:
                print("Rate limit detectado. Aguardando...")
                time.sleep(30)  # Aguardar 30 segundos
                continue
                
            response.raise_for_status()
            
            # Verificar se temos conteúdo
            if not response.content:
                print("Resposta vazia recebida")
                continue
            
            # Parse do HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Verificar se encontramos a tabela de publicações
            pub_table = soup.find('table', {'id': 'gsc_a_t'})
            if not pub_table:
                print("Tabela de publicações não encontrada")
                # Tentar método alternativo
                pub_rows = soup.find_all('tr', class_='gsc_a_tr')
            else:
                pub_rows = pub_table.find_all('tr', class_='gsc_a_tr')
            
            if not pub_rows:
                print("Nenhuma publicação encontrada")
                print("HTML snippet:", soup.get_text()[:500])
                continue
            
            print(f"Encontradas {len(pub_rows)} linhas de publicações")
            
            publications = []
            
            # Processar cada publicação
            for i, row in enumerate(pub_rows):
                try:
                    # Título e link
                    title_elem = row.find('a', class_='gsc_a_at')
                    if not title_elem:
                        print(f"Publicação {i+1}: Elemento de título não encontrado")
                        continue
                    
                    title = title_elem.get_text().strip()
                    href = title_elem.get('href', '')
                    link = "https://scholar.google.com" + href if href else '#'
                    
                    # Ano - tentar múltiplas formas
                    year_elem = row.find('span', class_='gsc_a_h')
                    if not year_elem:
                        # Tentar segunda coluna da tabela
                        year_elem = row.find('span', class_='gsc_a_y')
                    
                    year = year_elem.get_text().strip() if year_elem else 'N/A'
                    
                    # Validar se o ano é um número válido
                    try:
                        year_int = int(year) if year != 'N/A' and year else 0
                    except ValueError:
                        year_int = 0
                        year = 'N/A'
                    
                    print(f"Publicação {i+1}: {title[:50]}... ({year})")
                    
                    publications.append({
                        'title': title,
                        'year': year,
                        'year_int': year_int,
                        'link': link
                    })
                    
                except Exception as e:
                    print(f"Erro ao processar publicação {i+1}: {e}")
                    continue
            
            if publications:
                # Ordenar por ano decrescente
                publications.sort(key=lambda x: x['year_int'], reverse=True)
                print(f"✅ Sucesso! {len(publications)} publicações processadas")
                return publications
            else:
                print("Nenhuma publicação válida encontrada")
                continue
                
        except requests.exceptions.Timeout:
            print(f"Timeout na tentativa {attempt + 1}")
            time.sleep(10)
            continue
        except requests.exceptions.ConnectionError:
            print(f"Erro de conexão na tentativa {attempt + 1}")
            time.sleep(10)
            continue
        except requests.RequestException as e:
            print(f"Erro de requisição na tentativa {attempt + 1}: {e}")
            time.sleep(10)
            continue
        except Exception as e:
            print(f"Erro geral na tentativa {attempt + 1}: {e}")
            time.sleep(10)
            continue
    
    print(f"❌ Falha após {max_retries} tentativas")
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
