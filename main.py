import feedparser
from newspaper import Article
from epub_builder import create_epub
from mailer import send_epub

LIMIT = 10


def extract_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()

        return {
            "title": article.title,
            "link": url,
            "content": article.text.replace("\n", "<br/>"),
        }
    except Exception as e:
        print(f"Error leyendo {url}: {e}")
        return None


articles = []

with open("feeds.txt", encoding="utf-8") as f:
    feeds = [line.strip() for line in f if line.strip()]

for feed_url in feeds:
    feed = feedparser.parse(feed_url)

    print(f"Leyendo {feed.feed.get('title', feed_url)}")

    for entry in feed.entries[:LIMIT]:
        print(entry.title)

        article = extract_article(entry.link)

        if article:
            articles.append(article)

if not articles:
    raise Exception("No se ha podido descargar ningún artículo.")

print(f"Artículos descargados: {len(articles)}")

epub_file = create_epub(articles)

print(f"EPUB generado: {epub_file}")

send_epub(epub_file)

print("Proceso terminado.")
