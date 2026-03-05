"""Tests for LocalClaw"""
import pytest
import tempfile
from pathlib import Path

from localclaw.config import Config
from localclaw.tools import ToolRegistry
from localclaw.memory import Memory


class TestConfig:
    """Test configuration management"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = Config()
        assert config.model_name == "qwen2.5:7b"
        assert config.model_base_url == "http://localhost:11434/v1"
        assert config.workspace_path == "./workspace"
        assert config.restrict_to_workspace is True
    
    def test_custom_config(self, tmp_path):
        """Test loading custom config"""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
model:
  name: "llama3.2"
  base_url: "http://localhost:11434/v1"
  temperature: 0.5
  max_tokens: 2048

workspace:
  path: "./test_workspace"
  restrict_to_workspace: false
""")
        config = Config(str(config_file))
        assert config.model_name == "llama3.2"
        assert config.model_temperature == 0.5
        assert config.model_max_tokens == 2048
        assert config.restrict_to_workspace is False


class TestTools:
    """Test tool implementations"""
    
    @pytest.fixture
    def tool_registry(self, tmp_path):
        """Create a tool registry with temp workspace"""
        return ToolRegistry(str(tmp_path), restrict_to_workspace=True)
    
    def test_read_file(self, tool_registry, tmp_path):
        """Test reading a file"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        result = tool_registry.read_file("test.txt")
        assert "Hello, World!" in result
    
    def test_read_file_not_found(self, tool_registry):
        """Test reading non-existent file"""
        result = tool_registry.read_file("nonexistent.txt")
        assert "not found" in result.lower()
    
    def test_write_file(self, tool_registry, tmp_path):
        """Test writing a file"""
        result = tool_registry.write_file("output.txt", "Test content")
        assert "successfully" in result.lower()
        
        # Verify file was written
        assert (tmp_path / "output.txt").read_text() == "Test content"
    
    def test_list_dir(self, tool_registry, tmp_path):
        """Test listing directory"""
        # Create some files
        (tmp_path / "file1.txt").touch()
        (tmp_path / "dir1").mkdir()
        
        result = tool_registry.list_dir()
        assert "file1.txt" in result
        assert "dir1" in result
    
    def test_path_security(self, tool_registry):
        """Test path restriction security"""
        # Try to access file outside workspace
        result = tool_registry.read_file("../outside.txt")
        assert "access denied" in result.lower() or "outside" in result.lower()


class TestMemory:
    """Test memory system"""
    
    @pytest.fixture
    def memory(self, tmp_path):
        """Create a memory instance with temp db"""
        return Memory(str(tmp_path / "memory_db"), "test_collection")
    
    def test_save_memory(self, memory):
        """Test saving a memory"""
        memory_id = memory.save("Test content", "test_category")
        assert len(memory_id) == 12
        assert memory.get_stats()["total_memories"] == 1
    
    def test_search_memory(self, memory):
        """Test searching memories"""
        memory.save("Python programming tips", "coding")
        memory.save("Cooking recipes", "food")
        
        results = memory.search("python")
        assert len(results) == 1
        assert "Python" in results[0]["content"]
    
    def test_get_recent(self, memory):
        """Test getting recent memories"""
        memory.save("First", "test")
        memory.save("Second", "test")
        memory.save("Third", "test")
        
        recent = memory.get_recent(limit=2)
        assert len(recent) == 2


class TestIntegration:
    """Integration tests"""
    
    def test_full_workflow(self, tmp_path):
        """Test a complete workflow"""
        # Setup
        config = Config()
        tools = ToolRegistry(str(tmp_path), restrict_to_workspace=True)
        memory = Memory(str(tmp_path / "memory"))
        
        # Create a file
        tools.write_file("notes.txt", "Important notes")
        
        # Read it back
        content = tools.read_file("notes.txt")
        assert "Important notes" in content
        
        # Save to memory
        memory.save(content, "notes")
        
        # Search memory
        results = memory.search("notes")
        assert len(results) == 1
