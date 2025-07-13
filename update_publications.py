import requests
from scholarly import scholarly
from bs4 import BeautifulSoup

def get_google_scholar_articles(user_id, n=3):
    search_query = scholarly.search_author_id(user_id)
    author = scholarly.fill(search_query, sections=['publications'])
    pubs = author.get("publications", [])[:n]
    results = []
    for p in pubs:
        title = p['bib']['title']
        year = p['bib'].get('pub_year', 'n.d.')
        results.append(f"> 📘 **{title}**  \n> 🗓️ {year}")
    return results

def get_orcid_articles(orcid_id, n=3):
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    headers = {"Accept": "application/vnd.orcid+json"}
    response = requests.get(url, headers=headers)
    items = response.json().get("group", [])[:n]
    results = []
    for item in items:
        summary = item['work-summary'][0]
        title = summary['title']['title']['value']
        year = summary.get('publication-date', {}).get('year', {}).get('value', 'n.d.')
        doi = None
        for ext in summary.get('external-ids', {}).get('external-id', []):
            if ext.get('external-id-type') == 'doi':
                doi = ext.get('external-id-url', {}).get('value')
                break
        link = f"🔗 [View Publication]({doi})" if doi else ""
        results.append(f"> 📘 **{title}**  \n> 🗓️ {year} · {link}")
    return results

def get_researchgate_articles(profile_url, n=3):
    response = requests.get(profile_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    titles = [tag.get_text(strip=True) for tag in soup.select('a.nova-e-link--theme-bare') if tag.get('href', '').startswith('/publication')]
    return [f"> 📘 **{title}**" for title in titles[:n]]

def update_readme(publications):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    new_section = "\n\n".join(publications)
    updated = content.split("<!--PUBLICATIONS-->")
    content = f"{updated[0]}<!--PUBLICATIONS-->\n{new_section}\n<!--PUBLICATIONS-->{updated[2] if len(updated) > 2 else ''}"
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    scholar_id = "xNS8Qj4AAAAJ"
    orcid_id = "0000-0001-5667-0861"
    researchgate_url = "https://www.researchgate.net/profile/Caique-Kirilo"

    publications = []
    try:
        publications += get_google_scholar_articles(scholar_id)
    except Exception as e:
        publications.append(f"> ❌ Error loading Google Scholar: {e}")
    try:
        publications += get_orcid_articles(orcid_id)
    except Exception as e:
        publications.append(f"> ❌ Error loading ORCID: {e}")
    try:
        publications += get_researchgate_articles(researchgate_url)
    except Exception as e:
        publications.append(f"> ❌ Error loading ResearchGate: {e}")

    update_readme(publications[:3])
