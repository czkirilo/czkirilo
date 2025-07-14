import requests
from scholarly import scholarly
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def get_google_scholar_articles(user_id, n=3):
    logging.info("Fetching Google Scholar articles...")
    search_query = scholarly.search_author_id(user_id)
    author = scholarly.fill(search_query, sections=['publications'])
    pubs = author.get("publications", [])
    pubs_sorted = sorted(pubs, key=lambda x: x['bib'].get('pub_year', '0'), reverse=True)
    results = []
    for p in pubs_sorted[:n]:
        title = p['bib']['title']
        year = p['bib'].get('pub_year', 'n.d.')
        results.append(f"> 📘 **{title}**  \n> 🗓️ {year} · _(Google Scholar)_")
    return results

def get_orcid_articles(orcid_id, n=3):
    logging.info("Fetching ORCID articles...")
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    headers = {"Accept": "application/vnd.orcid+json"}
    response = requests.get(url, headers=headers)
    works = response.json().get("group", [])

    work_list = []
    for item in works:
        summary = item['work-summary'][0]
        title = summary['title']['title']['value']
        year = summary.get('publication-date', {}).get('year', {}).get('value', '0')
        doi = None
        for ext in summary.get('external-ids', {}).get('external-id', []):
            if ext.get('external-id-type') == 'doi':
                doi = ext.get('external-id-url', {}).get('value')
                break
        link = f"🔗 [View Publication]({doi})" if doi else ""
        work_list.append({
            "year": int(year) if year.isdigit() else 0,
            "text": f"> 📘 **{title}**  \n> 🗓️ {year} · {link} _(ORCID)_"
        })

    sorted_works = sorted(work_list, key=lambda x: x["year"], reverse=True)
    return [w["text"] for w in sorted_works[:n]]

def get_researchgate_articles(profile_url, n=3):
    logging.info("Fetching ResearchGate articles...")
    response = requests.get(profile_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    pub_links = soup.find_all('a', href=True)
    titles = []
    for tag in pub_links:
        href = tag.get('href')
        if '/publication/' in href and tag.text.strip():
            title = tag.text.strip()
            if title not in titles:
                titles.append(title)
        if len(titles) >= n:
            break
    return [f"> 📘 **{title}**  \n> _(ResearchGate)_" for title in titles[:n]]

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
        logging.error(f"Google Scholar error: {e}")
        publications.append(f"> ❌ Error loading Google Scholar: {e}")
    try:
        publications += get_orcid_articles(orcid_id)
    except Exception as e:
        logging.error(f"ORCID error: {e}")
        publications.append(f"> ❌ Error loading ORCID: {e}")
    try:
        publications += get_researchgate_articles(researchgate_url)
    except Exception as e:
        logging.error(f"ResearchGate error: {e}")
        publications.append(f"> ❌ Error loading ResearchGate: {e}")

    update_readme(publications[:3])

