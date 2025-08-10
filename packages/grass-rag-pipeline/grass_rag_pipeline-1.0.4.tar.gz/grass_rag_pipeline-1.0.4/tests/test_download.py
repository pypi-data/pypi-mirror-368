"""
Unit tests for model download manager
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from grass_rag.utils.download import ModelDownloadManager, InsufficientStorageError, NetworkError


class TestModelDownloadManager:
    """Test cases for ModelDownloadManager"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ModelDownloadManager(cache_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test manager initialization"""
        assert self.manager.cache_dir.exists()
        assert str(self.manager.cache_dir) == self.temp_dir
    
    def test_model_configs(self):
        """Test model configurations are valid"""
        configs = ModelDownloadManager.MODEL_CONFIGS
        
        assert "bge-m3" in configs
        assert "qwen3-0.6b" in configs
        
        for model_name, config in configs.items():
            assert "url" in config
            assert "files" in config
            assert "expected_size" in config
            assert "description" in config
            assert isinstance(config["files"], list)
            assert len(config["files"]) > 0
    
    def test_download_models(self):
        """Test model download process"""
        success = self.manager.download_models()
        assert success
        
        # Check that model directories were created
        for model_name in ModelDownloadManager.MODEL_CONFIGS.keys():
            model_dir = Path(self.temp_dir) / model_name
            assert model_dir.exists()
    
    def test_verify_models_success(self):
        """Test model verification when models are valid"""
        # First download models
        self.manager.download_models()
        
        # Then verify them
        assert self.manager.verify_models()
    
    def test_verify_models_missing(self):
        """Test model verification when models are missing"""
        # Don't download models first
        assert not self.manager.verify_models()
    
    def test_get_model_paths(self):
        """Test getting model paths"""
        # Initially no models
        paths = self.manager.get_model_paths()
        assert len(paths) == 0
        
        # After download
        self.manager.download_models()
        paths = self.manager.get_model_paths()
        
        assert len(paths) == len(ModelDownloadManager.MODEL_CONFIGS)
        for model_name in ModelDownloadManager.MODEL_CONFIGS.keys():
            assert model_name in paths
            assert Path(paths[model_name]).exists()
    
    def test_cleanup_old_models(self):
        """Test cleanup of old models"""
        # Download models first
        self.manager.download_models()
        
        # Corrupt one model by removing a file
        model_dir = Path(self.temp_dir) / "bge-m3"
        config_file = model_dir / "config.json"
        if config_file.exists():
            config_file.unlink()
        
        # Cleanup should remove corrupted model
        self.manager.cleanup_old_models()
        
        # Verify corrupted model was removed
        assert not model_dir.exists()
    
    def test_download_status_tracking(self):
        """Test download status tracking"""
        initial_status = self.manager.get_download_status()
        assert len(initial_status) == 0
        
        self.manager.download_models()
        
        final_status = self.manager.get_download_status()
        assert len(final_status) > 0
        
        for model_name in ModelDownloadManager.MODEL_CONFIGS.keys():
            assert model_name in final_status
            assert final_status[model_name] in ["downloaded", "cached", "failed"]
    
    def test_force_redownload(self):
        """Test force redownload functionality"""
        # Download once
        self.manager.download_models()
        status1 = self.manager.get_download_status()
        
        # Download again with force
        self.manager.download_models(force_redownload=True)
        status2 = self.manager.get_download_status()
        
        # All should be marked as downloaded, not cached
        for model_name in ModelDownloadManager.MODEL_CONFIGS.keys():
            assert status2[model_name] == "downloaded"


if __name__ == "__main__":
    pytest.main([__file__])