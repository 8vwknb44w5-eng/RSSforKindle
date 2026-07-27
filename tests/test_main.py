import pytest
from unittest.mock import MagicMock, patch
from src.main import main
from src.config import ContentSource

@patch("src.main.load_config")
@patch("src.main.DedupTracker")
@patch("src.main.get_fetcher")
@patch("src.main.process_results")
@patch("src.main.has_new_content")
@patch("src.main.EPUBGenerator")
@patch("src.main.SMTPSender")
@patch("src.main.get_logger")
def test_main_no_new_content(
    mock_get_logger,
    mock_sender,
    mock_generator,
    mock_has_new,
    mock_process,
    mock_fetcher,
    mock_tracker,
    mock_load_config
):
    # Setup
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger
    mock_config = MagicMock()
    mock_config.body = [ContentSource(type="rss", src="https://example.com/rss")]
    mock_load_config.return_value = mock_config
    
    mock_has_new.return_value = False
    
    # Run
    main()
    
    # Assert
    mock_load_config.assert_called_once()
    mock_has_new.assert_called_once()
    mock_generator.assert_not_called()
    mock_sender.assert_not_called()

@patch("src.main.load_config")
@patch("src.main.DedupTracker")
@patch("src.main.get_fetcher")
@patch("src.main.process_results")
@patch("src.main.has_new_content")
@patch("src.main.EPUBGenerator")
@patch("src.main.SMTPSender")
@patch("src.main.get_logger")
def test_main_failure(
    mock_get_logger,
    mock_sender,
    mock_generator,
    mock_has_new,
    mock_process,
    mock_fetcher,
    mock_tracker,
    mock_load_config
):
    # Setup
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger
    mock_load_config.side_effect = Exception("Config load failed")
    
    # Run
    with pytest.raises(SystemExit) as excinfo:
        main()
    
    # Assert
    assert excinfo.value.code == 1
    mock_logger.exception.assert_called()


@patch("src.main.load_config")
@patch("src.main.DedupTracker")
@patch("src.main.get_fetcher")
@patch("src.main.process_results")
@patch("src.main.has_new_content")
@patch("src.main.EPUBGenerator")
@patch("src.main.SMTPSender")
@patch("src.main.get_logger")
@patch("src.main.time.time")
def test_main_success(
    mock_time,
    mock_get_logger,
    mock_sender,
    mock_generator,
    mock_has_new,
    mock_process,
    mock_fetcher,
    mock_tracker,
    mock_load_config
):
    # Setup
    mock_time.return_value = 12345678.9
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger
    
    mock_config = MagicMock()
    mock_config.body = [ContentSource(type="rss", src="https://example.com/rss")]
    mock_config.title.get_plain_text.return_value = "Test Title"
    mock_load_config.return_value = mock_config
    
    mock_has_new.return_value = True
    
    mock_epub_generator = MagicMock()
    mock_epub_generator.generate.return_value = "dummy.epub"
    mock_generator.return_value = mock_epub_generator
    
    # Run
    with patch("src.uploader.webdav_uploader.WebDavUploader") as mock_webdav:
        main()
    
    # Assert
    mock_load_config.assert_called_once()
    mock_has_new.assert_called_once()
    mock_generator.assert_called_once_with(mock_config)
    mock_epub_generator.generate.assert_called_once_with(
        mock_process.return_value, [], start_time=12345678.9
    )
    mock_sender.assert_called_once()


@patch("src.main.load_config")
@patch("src.main.DedupTracker")
@patch("src.main.get_fetcher")
@patch("src.main.process_results")
@patch("src.main.has_new_content")
@patch("src.main.EPUBGenerator")
@patch("src.main.SMTPSender")
@patch("src.main.get_logger")
@patch("src.main.log_summary_table")
def test_main_raw_counts_isolation(
    mock_log_table,
    mock_get_logger,
    mock_sender,
    mock_generator,
    mock_has_new,
    mock_process,
    mock_fetcher,
    mock_tracker,
    mock_load_config
):
    # Setup two distinct ContentSource objects
    source1 = ContentSource(type="rss", src="https://example.com/rss1", priority=1)
    source2 = ContentSource(type="rss", src="https://example.com/rss2", priority=2)
    
    mock_config = MagicMock()
    mock_config.body = [source1, source2]
    mock_load_config.return_value = mock_config
    
    # Configure mock fetchers
    mock_fetcher_instance1 = MagicMock()
    mock_result1 = MagicMock()
    mock_result1.success = True
    mock_result1.articles = [MagicMock(), MagicMock(), MagicMock()]  # raw count = 3
    mock_fetcher_instance1.fetch_with_retry.return_value = mock_result1
    
    mock_fetcher_instance2 = MagicMock()
    mock_result2 = MagicMock()
    mock_result2.success = True
    mock_result2.articles = [MagicMock()]  # raw count = 1
    mock_fetcher_instance2.fetch_with_retry.return_value = mock_result2
    
    # Side effect for get_fetcher to return different fetchers for different sources
    def get_fetcher_side_effect(source, global_limit=15):
        if source == source1:
            return mock_fetcher_instance1
        return mock_fetcher_instance2
    mock_fetcher.side_effect = get_fetcher_side_effect
    
    # Mock deduplication results (e.g. source1 keeps 2 new articles, source2 keeps 0)
    mock_processed1 = MagicMock()
    mock_processed1.source = source1
    mock_processed1.success = True
    mock_processed1.articles = [MagicMock(), MagicMock()]  # new count = 2
    
    mock_processed2 = MagicMock()
    mock_processed2.source = source2
    mock_processed2.success = True
    mock_processed2.articles = []  # new count = 0
    
    mock_process.return_value = [mock_processed1, mock_processed2]
    mock_has_new.return_value = True
    
    # Run
    with patch("src.uploader.webdav_uploader.WebDavUploader") as mock_webdav:
        main()
        
    # Assert
    mock_log_table.assert_called_once()
    headers, rows = mock_log_table.call_args[0]
    
    assert len(rows) == 2
    # Row for source1: raw_c should be 3, new_c should be 2
    assert rows[0][1] == "rss"
    assert "rss1" in rows[0][2]
    assert rows[0][4] == 3  # Raw count
    assert rows[0][5] == 2  # New count
    
    # Row for source2: raw_c should be 1, new_c should be 0
    assert rows[1][1] == "rss"
    assert "rss2" in rows[1][2]
    assert rows[1][4] == 1  # Raw count
    assert rows[1][5] == 0  # New count


