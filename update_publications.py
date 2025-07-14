from scholarly import scholarly
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def get_google_scholar_articles(user_id, n=5):
    logging.info("Fetching articles from Google Scholar...")
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

def update_readme(publications):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    new_section = "\n\n".join(publications)
    updated = content.split("<!--PUBLICATIONS-->")
    content = f"{updated[0]}<!--PUBLICATIONS-->\n{new_section}\n<!--PUBLICATIONS-->{updated[2] if len(updated) > 2 else ''}"
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    scholar_id = "xNS8Qj4AAAAJ&hl"
    try:
        publications = get_google_scholar_articles(scholar_id)
        update_readme(publications)
        logging.info("README updated successfully.")
    except Exception as e:
        logging.error(f"Failed to update publications: {e}")


