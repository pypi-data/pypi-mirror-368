"""
Tests for attachment validation functionality.
"""

import os
import tempfile
import shutil
import pytest

from emailer_inao.utils.validators import CampaignValidator


class TestAttachmentValidation:
    """Test cases for attachment validation."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = CampaignValidator()
        self.attachments_dir = os.path.join(self.temp_dir, 'attachments')
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_test_file(self, filename: str, size_kb: int = 1):
        """Create a test file with specified size."""
        os.makedirs(self.attachments_dir, exist_ok=True)
        file_path = os.path.join(self.attachments_dir, filename)
        
        # Create file with specified size
        content = 'x' * (size_kb * 1024)
        with open(file_path, 'w') as f:
            f.write(content)
        
        return file_path
    
    def test_validate_attachments_no_folder(self):
        """Test validation when attachments folder doesn't exist."""
        result = self.validator.validate_attachments(self.attachments_dir)
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        assert result.total_size_bytes == 0
        assert len(result.attachment_files) == 0
    
    def test_validate_attachments_folder_is_file(self):
        """Test validation when 'attachments' exists but is a file."""
        # Create a file named 'attachments'
        with open(self.attachments_dir, 'w') as f:
            f.write('test')
        
        result = self.validator.validate_attachments(self.attachments_dir)
        
        assert not result.is_valid
        assert any('not a folder' in error for error in result.errors)
    
    def test_validate_attachments_empty_folder(self):
        """Test validation with empty attachments folder."""
        os.makedirs(self.attachments_dir)
        
        result = self.validator.validate_attachments(self.attachments_dir)
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert result.total_size_bytes == 0
        assert len(result.attachment_files) == 0
    
    def test_validate_attachments_valid_files(self):
        """Test validation with valid attachment files."""
        # Create test files
        self.create_test_file('document.pdf', 100)  # 100KB
        self.create_test_file('image.jpg', 200)     # 200KB
        
        result = self.validator.validate_attachments(self.attachments_dir)
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.attachment_files) == 2
        assert result.total_size_bytes > 0
    
    def test_validate_attachments_risky_file_types(self):
        """Test validation with potentially blocked file types."""
        # Create files with risky extensions
        self.create_test_file('program.exe', 10)
        self.create_test_file('script.bat', 5)
        self.create_test_file('archive.zip', 50)
        self.create_test_file('document.pdf', 10)  # Safe file
        
        result = self.validator.validate_attachments(self.attachments_dir)
        
        assert result.is_valid  # Still valid, just warnings
        assert len(result.errors) == 0
        assert len(result.warnings) >= 3  # At least 3 risky file warnings
        
        # Check that warnings mention the risky files
        warning_text = ' '.join(result.warnings)
        assert 'program.exe' in warning_text
        assert 'script.bat' in warning_text
        assert 'archive.zip' in warning_text
    
    def test_validate_attachments_missing_file(self):
        """Test validation when file is listed but doesn't exist."""
        os.makedirs(self.attachments_dir)
        
        # Create a broken symlink or reference to non-existent file
        # This is tricky to test directly, so we'll simulate by creating
        # and then deleting a file during validation
        file_path = self.create_test_file('temp.txt', 10)
        
        # Remove the file to simulate missing file
        os.remove(file_path)
        
        # Create another file that exists
        self.create_test_file('existing.txt', 10)
        
        result = self.validator.validate_attachments(self.attachments_dir)
        
        # Should still be valid since we only have the existing file
        assert result.is_valid
        assert len(result.attachment_files) == 1
    
    def test_validate_attachments_size_warning(self):
        """Test validation with files that trigger size warning (15MB)."""
        # Create a file that's about 11MB (will trigger warning after base64 overhead)
        # 11MB * 1.37 + overhead ≈ 15.1MB (just over 15MB threshold)
        self.create_test_file('large_file.pdf', 11 * 1024)  # 11MB
        
        result = self.validator.validate_attachments(self.attachments_dir)
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.warnings) >= 1
        
        # Check that warning mentions size and provides guidance
        warning_text = ' '.join(result.warnings)
        assert 'WARNING' in warning_text
        assert 'MB' in warning_text
        assert 'Gmail' in warning_text  # Should mention provider limits
    
    def test_validate_attachments_size_alarm(self):
        """Test validation with files that trigger size alarm (20MB)."""
        # Create a file that's about 22MB (will trigger alarm)
        self.create_test_file('huge_file.pdf', 22 * 1024)  # 22MB
        
        result = self.validator.validate_attachments(self.attachments_dir)
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.warnings) >= 1
        
        # Check that warning mentions alarm and delivery risks
        warning_text = ' '.join(result.warnings)
        assert 'ALARM' in warning_text
        assert 'delivery failures' in warning_text
        assert 'splitting' in warning_text  # Should suggest splitting
    
    def test_validate_attachments_multiple_files_combined_size(self):
        """Test validation where multiple small files combine to large size."""
        # Create multiple files that together exceed 15MB
        for i in range(10):
            self.create_test_file(f'file_{i}.pdf', 2 * 1024)  # 2MB each = 20MB total
        
        result = self.validator.validate_attachments(self.attachments_dir)
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.warnings) >= 1
        assert len(result.attachment_files) == 10
        
        # Should trigger alarm due to combined size
        warning_text = ' '.join(result.warnings)
        assert 'ALARM' in warning_text
    
    def test_validate_attachments_ignores_subdirectories(self):
        """Test that validation ignores subdirectories in attachments folder."""
        os.makedirs(self.attachments_dir)
        
        # Create a file
        self.create_test_file('document.pdf', 10)
        
        # Create a subdirectory with files
        subdir = os.path.join(self.attachments_dir, 'subfolder')
        os.makedirs(subdir)
        with open(os.path.join(subdir, 'ignored.txt'), 'w') as f:
            f.write('This should be ignored')
        
        result = self.validator.validate_attachments(self.attachments_dir)
        
        assert result.is_valid
        assert len(result.attachment_files) == 1  # Only the PDF, not the file in subfolder
        assert 'document.pdf' in result.attachment_files[0]
    
    def test_calculate_estimated_email_size(self):
        """Test email size calculation with base64 overhead."""
        # Test with known size
        attachment_size = 1024 * 1024  # 1MB
        estimated_size = self.validator._calculate_estimated_email_size(attachment_size)
        
        # Should be larger than original due to base64 encoding and MIME overhead
        assert estimated_size > attachment_size
        
        # Should be approximately 37% larger plus some overhead
        expected_min = attachment_size * 1.3  # At least 30% larger
        expected_max = attachment_size * 1.5  # At most 50% larger
        assert expected_min <= estimated_size <= expected_max
    
    def test_validate_attachments_permission_denied(self):
        """Test validation when file exists but cannot be read."""
        if os.name == 'nt':  # Skip on Windows as permission handling is different
            pytest.skip("Permission test not reliable on Windows")
        
        os.makedirs(self.attachments_dir)
        file_path = self.create_test_file('restricted.pdf', 10)
        
        # Remove read permission
        os.chmod(file_path, 0o000)
        
        try:
            result = self.validator.validate_attachments(self.attachments_dir)
            
            # Should have error about not being able to read the file
            assert not result.is_valid
            assert any('Cannot read' in error for error in result.errors)
            
        finally:
            # Restore permissions for cleanup
            os.chmod(file_path, 0o644)
    
    def test_risky_extensions_list(self):
        """Test that all expected risky extensions are in the list."""
        expected_risky = {'.exe', '.bat', '.cmd', '.zip', '.jar', '.vbs', '.js'}
        
        for ext in expected_risky:
            assert ext in self.validator.RISKY_EXTENSIONS
    
    def test_size_thresholds(self):
        """Test that size thresholds are set correctly."""
        assert self.validator.SIZE_WARNING_THRESHOLD == 15 * 1024 * 1024  # 15MB
        assert self.validator.SIZE_ALARM_THRESHOLD == 20 * 1024 * 1024    # 20MB
