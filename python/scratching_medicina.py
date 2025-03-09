import requests
from bs4 import BeautifulSoup
from newspaper import Article
import time
from urllib.parse import urljoin, urlparse

# Lista de medios españoles con secciones de medicina/noticias
NEWS_SITES = [
    "https://www.defensa.com",
    "https://galaxiamilitar.es",
    "https://elpais.com/noticias/ejercito-espanol/",
]

# Archivo donde se guardarán los artículos (solo primer párrafo)
OUTPUT_FILE = "noticias_completas_militar2.txt"

def get_article_links(page_url, max_links=50):
    """
    Extrae enlaces de artículos desde la página dada.
    Se forma la URL absoluta y se filtra por palabras clave,
    descartando enlaces a recursos (imágenes, PDF, etc.) y los que sean solo el homepage.
    """
    try:
        response = requests.get(page_url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    except Exception as e:
        print(f"Error al obtener enlaces de {page_url}: {e}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    links = set()
    
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        full_url = urljoin(page_url, href)
        parsed = urlparse(full_url)
        # Descarta si es solo el dominio o si no tiene ruta suficiente
        if parsed.path in ["", "/"]:
            continue
        # Descarta enlaces a recursos multimedia o archivos
        if full_url.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".pdf", ".svg")):
            continue
        # Filtrar por palabras clave indicativas de artículos
        if any(keyword in full_url.lower() for keyword in ["militar", "ejercito", "guerra", "maniobras", "armada", "defensa"]):
            links.add(full_url)
        if len(links) >= max_links:
            break
    return list(links)

def extract_article_info(url, min_length=50):
    """
    Extrae el primer párrafo de un artículo usando newspaper3k.
    Se divide el texto del artículo por saltos de línea y se toma el primer párrafo no vacío.
    Se descarta el artículo si el primer párrafo es muy corto.
    """
    try:
        article = Article(url, language='es')
        article.download()
        article.parse()
        text = article.text.strip()
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        if paragraphs:
            first_paragraph = paragraphs[0]
            # Si el primer párrafo es demasiado corto, lo consideramos no relevante
            if len(first_paragraph) < min_length:
                return None, url
            return first_paragraph, url
        else:
            return None, url
    except Exception as e:
        print(f"Error al extraer contenido de {url}: {e}")
        return None, url

def save_articles(articles):
    """
    Guarda en un archivo de texto cada artículo, solo su primer párrafo.
    Cada noticia se separa de la siguiente con una línea que contiene un punto.
    """
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for first_paragraph, url in articles:
            f.write(first_paragraph + "\n")
            f.write("\n")
    print(f"Se han guardado {len(articles)} artículos en {OUTPUT_FILE}")

def main():
    all_articles = []
    for site in NEWS_SITES:
        print(f"Procesando sitio: {site}")
        article_links = get_article_links(site, max_links=40)
        print(f"Encontrados {len(article_links)} enlaces en {site}")
        for link in article_links:
            first_paragraph, url = extract_article_info(link)
            if first_paragraph:
                all_articles.append((first_paragraph, url))
                print(f"Artículo añadido desde: {url}")
            else:
                print(f"Contenido insuficiente o no se pudo extraer de: {link}")
            time.sleep(1)  # Pequeña pausa para no saturar el servidor
        time.sleep(2)
    save_articles(all_articles)

if __name__ == "__main__":
    main()
