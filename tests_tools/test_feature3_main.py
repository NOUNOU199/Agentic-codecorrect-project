"""
Tests for Feature 3: main.py Entry Point
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import patch, Mock

sys.path.insert(0, str(Path(__file__).parent.parent))

# Import after adding to path
import main as main_module


class TestMainEntryPoint:
    """Test main.py entry point"""
    
    def test_parse_arguments_with_target_dir(self):
        """Test argument parsing"""
        test_args = ['main.py', '--target_dir', 'sandbox/']
        with patch.object(sys, 'argv', test_args):
            args = main_module.parse_arguments()
            assert args.target_dir == 'sandbox/'
    
    def test_parse_arguments_missing_target_dir(self):
        """Test argument parsing fails without target_dir"""
        test_args = ['main.py']
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit):
                main_module.parse_arguments()
    
    def test_validate_existing_directory(self):
        """Test validation of existing directory"""
        # Create temp directory
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            result = main_module.validate_target_directory(temp_dir)
            assert result is True
    
    def test_validate_nonexistent_directory(self):
        """Test validation of non-existent directory"""
        result = main_module.validate_target_directory('/nonexistent/path/xyz')
        assert result is False
    
    def test_validate_file_not_directory(self):
        """Test validation rejects files"""
        import tempfile
        with tempfile.NamedTemporaryFile() as temp_file:
            result = main_module.validate_target_directory(temp_file.name)
            assert result is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
