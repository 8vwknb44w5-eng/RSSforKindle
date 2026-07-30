from ebooklib import epub


def create_epub(articles, output_file="kindle.epub"):
    book = epub.EpubBook()

    book.set_identifier("rss-kindle")
    book.set_title("RSS Digest")
    book.set_language("en")
    book.add_author("RSS for Kindle")

    chapters = []

    for i, article in enumerate(articles):
        chapter = epub.EpubHtml(
            title=article["title"],
            file_name=f"chapter_{i}.xhtml",
            lang="en",
        )

        chapter.content = f"""
<h1>{article['title']}</h1>
<p><a href="{article['link']}">{article['link']}</a></p>
<hr/>
{article['content']}
"""

        book.add_item(chapter)
        chapters.append(chapter)

    book.toc = chapters
    book.spine = ["nav"] + chapters

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    style = """
body {
    font-family: serif;
    margin: 5%;
}
"""

    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=style,
    )

    book.add_item(nav_css)

    epub.write_epub(output_file, book)

    return output_file
