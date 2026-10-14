import os
import re
import time
from urllib.parse import urljoin, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# Configuration
OUTPUT_DIR = "website-archives"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_article_links(base_url):
    """Collect article URLs from the paginated blog."""
    article_links = set()
    page = 1

    print("🔍 Récupération de la liste des liens d'articles...")
    while True:
        if page == 1:
            url = base_url
        else:
            url = urljoin(base_url, f"page/{page}/")

        print(f"Inspection de la page {page} : {url}")
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            print(f"Fin de la pagination ou erreur (Code {response.status_code}).")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        base_parts = urlsplit(base_url)
        base_path = base_parts.path
        links = soup.find_all('a', href=True)
        found_on_page = 0

        for link in links:
            article_url = urljoin(url, link['href'])
            article_parts = urlsplit(article_url)
            article_path = article_parts.path
            if (
                article_parts.netloc == base_parts.netloc
                and article_path.startswith(base_path)
                and article_path.rstrip('/') != base_path.rstrip('/')
                and not re.search(r'/page/\d+/?$', article_path)
                and any(char.isdigit() for char in article_path.rstrip('/').split('/')[-2:])
            ):
                article_url = urlunsplit(article_parts._replace(fragment=''))
                if article_url not in article_links:
                    article_links.add(article_url)
                    found_on_page += 1

        if found_on_page == 0 and page > 1:
            break

        page += 1
        time.sleep(0.5)

    print(f"✅ Total d'articles uniques trouvés : {len(article_links)}")
    return list(article_links)

def scrape_and_convert(links):
    """Download each article, convert it to Markdown, and save it."""
    print("\n🚀 Début du rapatriement et de la conversion...")

    for i, url in enumerate(links, 1):
        print(f"[{i}/{len(links)}] Traitement : {url}")
        try:
            response = requests.get(url, headers=HEADERS)
            if response.status_code != 200:
                print(f"❌ Erreur {response.status_code} sur {url}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            title_elem = soup.find('h1')
            title = title_elem.get_text().strip() if title_elem else "Sans titre"

            date_elem = soup.find('time') or soup.find(class_='date')
            date_str = date_elem.get_text().strip() if date_elem else ""

            content_elem = soup.find('article') or soup.find(class_='post-content') or soup.find(class_='entry-content')

            if not content_elem:
                print(f"⚠️ Contenu principal introuvable pour {url}, passage.")
                continue

            markdown_body = md(str(content_elem), heading_style="ATX")
            escaped_title = title.replace('"', '\\"')

            frontmatter = f"""---
            title: "{escaped_title}"
            date: "{date_str}"
            source_url: "{url}"
            ---

            """

            slug = url.rstrip('/').split('/')[-1]
            if not slug:
                slug = f"article-{i}"
            filename = os.path.join(OUTPUT_DIR, f"{slug}.md")

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(frontmatter + markdown_body)

        except Exception as e:
            print(f"❌ Erreur critique sur {url} : {e}")

        time.sleep(0.3)

def get_base_url():
    while True:
        value = input("Enter the blog URL to scrape: ").strip()
        parts = urlsplit(value)
        if parts.scheme in ('http', 'https') and parts.netloc:
            path = parts.path.rstrip('/') + '/'
            return urlunsplit((parts.scheme, parts.netloc, path, '', ''))
        print("Please enter a valid URL starting with http:// or https://.")

if __name__ == "__main__":
    base_url = get_base_url()
    links = get_article_links(base_url)
    if links:
        scrape_and_convert(links)
        print(f"\n✨ Opération terminée ! Vos fichiers sont dans le dossier '{OUTPUT_DIR}'.")
    else:
        print("Aucun lien trouvé. Vérifiez la structure de la page et l'URL saisie.")