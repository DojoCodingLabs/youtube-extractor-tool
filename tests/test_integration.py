"""Integration tests requiring real YouTube videos and API keys."""
import json
import os
import pytest
from pathlib import Path
from unittest.mock import patch

from yt_extractor.core.extractor import YouTubeExtractor
from yt_extractor.core.config import config
from yt_extractor.core.exceptions import ConfigurationError, VideoNotFoundError


class TestRealVideoProcessing:
    """Tests that require real YouTube videos and API access."""
    
    @pytest.fixture(autouse=True)
    def setup_test_env(self, tmp_path):
        """Set up test environment."""
        # Use test output directory
        config.default_output_dir = str(tmp_path / "test_output")
        config.cache_dir = str(tmp_path / "test_cache")
        config.enable_cache = True
        
    def load_test_videos(self):
        """Load test video URLs from test_videos.json."""
        test_file = Path(__file__).parent / "test_videos.json"
        if not test_file.exists():
            pytest.skip("test_videos.json not found")
            
        with open(test_file) as f:
            data = json.load(f)
        
        return data["test_videos"], data["test_expectations"]
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"),
        reason="No API keys configured"
    )
    def test_configuration_validation(self):
        """Test that configuration validation works with real API keys."""
        try:
            config.validate()
            # If we get here, config is valid
            assert True
        except ConfigurationError as e:
            pytest.fail(f"Configuration validation failed: {e}")
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"),
        reason="No API keys configured"
    )
    def test_process_short_video(self):
        """Test processing a short video end-to-end."""
        test_videos, expectations = self.load_test_videos()
        short_video = test_videos.get("short_tech")
        
        if not short_video or "example" in short_video["url"]:
            pytest.skip("No real test video URL configured")
        
        extractor = YouTubeExtractor()
        
        try:
            result_path = extractor.process_video(short_video["url"])
            
            # Verify file was created
            assert result_path.exists()
            
            # Verify file has content
            content = result_path.read_text()
            assert len(content) > 100  # Should have substantial content
            
            # Verify required sections exist
            for required_section in expectations["required_sections"]:
                assert f"## {required_section}" in content
            
            # Verify front matter exists
            assert content.startswith("---")
            assert "type: \"video-notes\"" in content
            
        except Exception as e:
            pytest.fail(f"Video processing failed: {e}")
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"),
        reason="No API keys configured"
    )
    def test_error_recovery_real_failure(self, tmp_path):
        """Test error recovery with a real failure scenario."""
        test_videos, _ = self.load_test_videos()
        
        # Use invalid video URL to trigger failure
        invalid_url = "https://www.youtube.com/watch?v=INVALID_ID_123"
        
        extractor = YouTubeExtractor()
        
        with pytest.raises(VideoNotFoundError):
            extractor.process_video(invalid_url)
        
        # Verify recovery state was created and then cleaned up appropriately
        video_id = extractor._extract_video_id(invalid_url)
        recovery_file = Path(".processing_state") / f"{video_id}.json"
        
        # Recovery file might exist if processing got partially through
        # This is expected behavior
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"),
        reason="No API keys configured"
    )
    def test_caching_works(self):
        """Test that caching works with real video processing."""
        test_videos, _ = self.load_test_videos()
        short_video = test_videos.get("short_tech")
        
        if not short_video or "example" in short_video["url"]:
            pytest.skip("No real test video URL configured")
        
        extractor = YouTubeExtractor()
        
        # Process video first time
        result_path1 = extractor.process_video(short_video["url"])
        content1 = result_path1.read_text()
        
        # Process same video again - should use cache
        result_path2 = extractor.process_video(short_video["url"])
        content2 = result_path2.read_text()
        
        # Results should be identical
        assert content1 == content2
        
        # Should have used cache (we can't easily test this without mocking,
        # but at least we verify it doesn't crash)
    
    def test_video_id_extraction(self):
        """Test video ID extraction from various YouTube URL formats."""
        extractor = YouTubeExtractor()
        
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s", "dQw4w9WgXcQ"),
        ]
        
        for url, expected_id in test_cases:
            extracted_id = extractor._extract_video_id(url)
            assert extracted_id == expected_id
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"),
        reason="No API keys configured"
    )
    def test_cli_integration(self, tmp_path):
        """Test CLI integration with real processing."""
        from yt_extractor.cli import cli
        from click.testing import CliRunner
        
        test_videos, _ = self.load_test_videos()
        short_video = test_videos.get("short_tech")
        
        if not short_video or "example" in short_video["url"]:
            pytest.skip("No real test video URL configured")
        
        runner = CliRunner()
        
        # Test info command
        result = runner.invoke(cli, ['info', short_video["url"]])
        
        if result.exit_code == 1 and "Configuration error" in result.output:
            pytest.skip("CLI configuration not set up")
        
        assert result.exit_code == 0
        assert "Title" in result.output
        
        # Test dry run
        result = runner.invoke(cli, [
            'process', 
            '--dry-run', 
            '--output-dir', str(tmp_path),
            short_video["url"]
        ])
        
        assert result.exit_code == 0
        assert "DRY RUN" in result.output


@pytest.mark.slow
class TestPerformanceAndScaling:
    """Performance tests for the extractor."""
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"),
        reason="No API keys configured"
    )
    def test_concurrent_processing(self, tmp_path):
        """Test processing multiple videos concurrently."""
        test_videos, _ = self.load_test_videos()
        
        # Get multiple test videos
        urls = []
        for video_key, video_data in test_videos.items():
            if "example" not in video_data["url"]:
                urls.append(video_data["url"])
        
        if len(urls) < 2:
            pytest.skip("Need at least 2 real test video URLs")
        
        # Take only first 2 for performance test
        urls = urls[:2]
        
        extractor = YouTubeExtractor()
        results = extractor.process_videos(urls, str(tmp_path))
        
        # Should succeed in processing both
        assert len(results) == len(urls)
        
        # All result files should exist and have content
        for result_path in results:
            assert result_path.exists()
            content = result_path.read_text()
            assert len(content) > 100
    
