
import pytest
from unittest.mock import MagicMock, patch
from bs4 import BeautifulSoup
from ebooklib import epub

from src.epub.generator import EPUBGenerator
from src.config import ContentSource, Config, _parse_config
from src.fetchers.base import Article, FetchResult
from src.processors.content_processor import ContentProcessor

class TestImageToggle:
    """Tests for the load_images configuration toggle."""

    @pytest.fixture
    def mock_image_processor(self):
        with patch('src.epub.generator.ImageProcessor') as mock:
            processor = mock.return_value
            processor.download_and_process.return_value = ("test.jpg", b"fake_data")
            yield processor

    def test_global_toggle_off(self, mock_image_processor):
        """Test that images are skipped when global load_images is 'N'."""
        config_data = {
            "title": {"text": "Test", "img": ""},
            "load_images": "N",
            "body": [{"type": "web", "src": "https://example.com", "title": "Test"}]
        }
        config = _parse_config(config_data)
        generator = EPUBGenerator(config)
        
        article = Article(
            title="Test",
            content='<div><img src="https://example.com/test.jpg"></div>',
            url="https://example.com"
        )
        
        # We don't want to run the full generate() as it does a lot of things
        # Just test _add_chapters
        book = epub.EpubBook()
        sections = [(config.body[0], [article], "Test")]
        unique_emojis = set()
        
        generator._add_chapters(book, sections, unique_emojis)
        
        # Check that download_and_process was NOT called
        mock_image_processor.download_and_process.assert_not_called()
        
        # Check that img tag was removed
        # book.items contains [divider, chapter]
        chapters = [item for item in book.items if isinstance(item, epub.EpubHtml) and "chapter" in item.file_name]
        soup = BeautifulSoup(chapters[0].content, 'lxml')
        assert soup.find('img') is None

    def test_source_toggle_off(self, mock_image_processor):
        """Test that images are skipped when per-source load_images is 'N'."""
        config_data = {
            "title": {"text": "Test", "img": ""},
            "load_images": "Y",
            "body": [
                {"type": "web", "src": "https://example.com/1", "title": "Load", "load_images": "Y"},
                {"type": "web", "src": "https://example.com/2", "title": "Skip", "load_images": "N"}
            ]
        }
        config = _parse_config(config_data)
        generator = EPUBGenerator(config)
        
        article1 = Article(
            title="Load",
            content='<div><img src="https://example.com/img1.jpg"></div>',
            url="https://example.com/1"
        )
        article2 = Article(
            title="Skip",
            content='<div><img src="https://example.com/img2.jpg"></div>',
            url="https://example.com/2"
        )
        
        book = epub.EpubBook()
        sections = [
            (config.body[0], [article1], "Load"),
            (config.body[1], [article2], "Skip")
        ]
        unique_emojis = set()
        
        generator._add_chapters(book, sections, unique_emojis)
        
        # Should be called once for article1
        assert mock_image_processor.download_and_process.call_count == 1
        
        # Check first chapter has image
        chapters = [item for item in book.items if isinstance(item, epub.EpubHtml) and "chapter" in item.file_name]
        
        # Find Load chapter
        load_chapter = next(c for c in chapters if c.title == "Load")
        skip_chapter = next(c for c in chapters if c.title == "Skip")
        
        soup1 = BeautifulSoup(load_chapter.content, 'lxml')
        assert soup1.find('img') is not None
        assert "images/" in soup1.find('img')['src']
        
        soup2 = BeautifulSoup(skip_chapter.content, 'lxml')
        assert soup2.find('img') is None

    def test_emoji_still_loaded(self, mock_image_processor):
        """Test that emojis are still rendered even if load_images is 'N'."""
        config_data = {
            "title": {"text": "Test 🚀", "img": ""},
            "load_images": "N",
            "body": [{"type": "web", "src": "https://example.com", "title": "Test 🚀"}]
        }
        config = _parse_config(config_data)
        generator = EPUBGenerator(config)
        
        # Wrap emojis in content as ContentProcessor would
        article = Article(
            title="Title 🚀",
            content=ContentProcessor.wrap_emojis('<div>Body ✨ <img src="https://example.com/test.jpg"></div>'),
            url="https://example.com"
        )
        
        book = epub.EpubBook()
        sections = [(config.body[0], [article], "Test")]
        unique_emojis = set()
        
        # We need to mock render_emoji_to_png
        with patch('src.utils.emoji_renderer.render_emoji_to_png', side_effect=lambda e, f, t: f"emoji_{hex(ord(e))}.png"):
            with patch('builtins.open', MagicMock()):
                generator._add_chapters(book, sections, unique_emojis)
                generator._add_rendered_emojis(book, unique_emojis)
        
        # Check that normal image is gone
        chapters = [item for item in book.items if isinstance(item, epub.EpubHtml) and "chapter" in item.file_name]
        soup = BeautifulSoup(chapters[0].content, 'lxml')
        img_tags = soup.find_all('img')
        
        # Should contain two emoji images: 🚀 in h1, ✨ in content
        assert len(img_tags) == 2
        for img in img_tags:
            assert 'emoji' in img.get('class', [])
        
        # Normal image should be gone
        assert not any('test.jpg' in img['src'] for img in img_tags)
