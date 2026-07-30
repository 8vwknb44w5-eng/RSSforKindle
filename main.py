import feedparser

LIMIT = 15

with open("feeds.txt", "r", encoding="utf-8") as f:
    feeds = [line.strip() for line in f if line.strip()]

for url in feeds:
    feed = feedparser.parse(url)

    print("=" * 80)
    print(feed.feed.get("title", url))
    print("=" * 80)

    for entry in feed.entries[:LIMIT]:
        print(entry.title)
        print(entry.link)
        print()
