"""
Tests for validation functionality.
"""

import os
import tempfile
import shutil
import pytest

from emailer_inao.utils.validators import CampaignValidator, validate_campaign_folder


class TestCampaignValidator:
    """Test cases for CampaignValidator class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = CampaignValidator()
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_validate_missing_files(self):
        """Test validation with missing required files."""
        result = self.validator.validate_campaign_folder(self.temp_dir)
        
        assert not result.is_valid
        assert len(result.errors) == 3
        assert any('recipients.csv' in error for error in result.errors)
        assert any('msg.txt' in error for error in result.errors)
        assert any('subject.txt' in error for error in result.errors)
    
    def test_validate_directory_instead_of_file(self):
        """Test validation when directory exists instead of file."""
        # Create directory with same name as required file
        os.makedirs(os.path.join(self.temp_dir, 'recipients.csv'))
        
        result = self.validator.validate_campaign_folder(self.temp_dir)
        
        assert not result.is_valid
        assert any('is not a file' in error for error in result.errors)
    
    def test_validate_empty_csv(self):
        """Test validation with empty CSV file."""
        # Create empty files
        open(os.path.join(self.temp_dir, 'recipients.csv'), 'w').close()
        open(os.path.join(self.temp_dir, 'msg.txt'), 'w').close()
        open(os.path.join(self.temp_dir, 'subject.txt'), 'w').close()
        
        result = self.validator.validate_campaign_folder(self.temp_dir)
        
        assert not result.is_valid
        assert any('empty' in error for error in result.errors)
    
    def test_validate_csv_missing_email_column(self):
        """Test validation with CSV missing email column."""
        # Create CSV without email column
        csv_content = "name,company\nJohn Doe,ACME Corp"
        with open(os.path.join(self.temp_dir, 'recipients.csv'), 'w') as f:
            f.write(csv_content)
        
        # Create other files
        with open(os.path.join(self.temp_dir, 'msg.txt'), 'w') as f:
            f.write("Hello {{name}}")
        with open(os.path.join(self.temp_dir, 'subject.txt'), 'w') as f:
            f.write("Welcome {{name}}")
        
        result = self.validator.validate_campaign_folder(self.temp_dir)
        
        assert not result.is_valid
        assert any('email' in error and 'column' in error for error in result.errors)
    
    def test_validate_invalid_email_addresses(self):
        """Test validation with invalid email addresses."""
        csv_content = """email,name
invalid-email,John Doe
john@,Jane Smith
@example.com,Bob Johnson
valid@example.com,Alice Brown"""
        
        with open(os.path.join(self.temp_dir, 'recipients.csv'), 'w') as f:
            f.write(csv_content)
        
        with open(os.path.join(self.temp_dir, 'msg.txt'), 'w') as f:
            f.write("Hello {{name}}")
        with open(os.path.join(self.temp_dir, 'subject.txt'), 'w') as f:
            f.write("Welcome {{name}}")
        
        result = self.validator.validate_campaign_folder(self.temp_dir)
        
        assert not result.is_valid
        # Should have 3 invalid email errors
        invalid_email_errors = [e for e in result.errors if 'Invalid email' in e]
        assert len(invalid_email_errors) == 3
    
    def test_validate_duplicate_emails(self):
        """Test validation with duplicate email addresses."""
        csv_content = """email,name
john@example.com,John Doe
jane@example.com,Jane Smith
john@example.com,John Duplicate"""
        
        with open(os.path.join(self.temp_dir, 'recipients.csv'), 'w') as f:
            f.write(csv_content)
        
        with open(os.path.join(self.temp_dir, 'msg.txt'), 'w') as f:
            f.write("Hello {{name}}")
        with open(os.path.join(self.temp_dir, 'subject.txt'), 'w') as f:
            f.write("Welcome {{name}}")
        
        result = self.validator.validate_campaign_folder(self.temp_dir)
        
        assert not result.is_valid
        assert any('Duplicate email' in error for error in result.errors)
    
    def test_validate_duplicate_primary_keys(self):
        """Test validation with duplicate primary keys."""
        csv_content = """id,email,name
1,john@example.com,John Doe
2,jane@example.com,Jane Smith
1,bob@example.com,Bob Johnson"""
        
        with open(os.path.join(self.temp_dir, 'recipients.csv'), 'w') as f:
            f.write(csv_content)
        
        with open(os.path.join(self.temp_dir, 'msg.txt'), 'w') as f:
            f.write("Hello {{name}}")
        with open(os.path.join(self.temp_dir, 'subject.txt'), 'w') as f:
            f.write("Welcome {{name}}")
        
        result = self.validator.validate_campaign_folder(self.temp_dir)
        
        assert not result.is_valid
        assert any('Duplicate primary key' in error for error in result.errors)
    
    def test_validate_template_invalid_references(self):
        """Test validation with invalid template references."""
        csv_content = """email,name,company
john@example.com,John Doe,ACME Corp"""
        
        with open(os.path.join(self.temp_dir, 'recipients.csv'), 'w') as f:
            f.write(csv_content)
        
        # Template with invalid reference
        with open(os.path.join(self.temp_dir, 'msg.txt'), 'w') as f:
            f.write("Hello {{name}}, welcome to {{invalid_field}}")
        with open(os.path.join(self.temp_dir, 'subject.txt'), 'w') as f:
            f.write("Welcome {{nonexistent}}")
        
        result = self.validator.validate_campaign_folder(self.temp_dir)
        
        assert not result.is_valid
        template_errors = [e for e in result.errors if 'Template reference' in e]
        assert len(template_errors) == 2  # One for each invalid reference
    
    def test_validate_successful_campaign(self):
        """Test validation with a valid campaign folder."""
        csv_content = """email,name,company
john@example.com,John Doe,ACME Corp
jane@example.com,Jane Smith,Tech Inc"""
        
        with open(os.path.join(self.temp_dir, 'recipients.csv'), 'w') as f:
            f.write(csv_content)
        
        with open(os.path.join(self.temp_dir, 'msg.txt'), 'w') as f:
            f.write("Dear {{name}},\n\nWelcome to {{company}}!\n\nBest regards")
        with open(os.path.join(self.temp_dir, 'subject.txt'), 'w') as f:
            f.write("Welcome {{name}} to our service")
        
        result = self.validator.validate_campaign_folder(self.temp_dir)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_with_warnings(self):
        """Test validation that produces warnings but is still valid."""
        csv_content = """email,name,company,unused_field
john@example.com,John Doe,ACME Corp,unused_value"""
        
        with open(os.path.join(self.temp_dir, 'recipients.csv'), 'w') as f:
            f.write(csv_content)
        
        # Template that doesn't use all fields
        with open(os.path.join(self.temp_dir, 'msg.txt'), 'w') as f:
            f.write("Dear {{name}}")
        with open(os.path.join(self.temp_dir, 'subject.txt'), 'w') as f:
            f.write("Welcome {{name}}")
        
        result = self.validator.validate_campaign_folder(self.temp_dir)
        
        assert result.is_valid
        assert len(result.errors) == 0
        # Note: Unused field warnings are handled by template processor, not validator
    
    def test_is_valid_email(self):
        """Test email validation function."""
        # Valid emails
        assert self.validator._is_valid_email('user@example.com')
        assert self.validator._is_valid_email('test.email+tag@domain.co.uk')
        assert self.validator._is_valid_email('user123@test-domain.org')
        
        # Invalid emails
        assert not self.validator._is_valid_email('invalid-email')
        assert not self.validator._is_valid_email('user@')
        assert not self.validator._is_valid_email('@domain.com')
        assert not self.validator._is_valid_email('user@domain')
        assert not self.validator._is_valid_email('')
    
    def test_extract_template_references(self):
        """Test template reference extraction."""
        template = "Hello {{name}}, welcome to {{company}}! Your ID is {{user_id}}."
        
        references = self.validator._extract_template_references(template)
        
        expected = {'name', 'company', 'user_id'}
        assert references == expected
    
    def test_extract_template_references_with_spaces(self):
        """Test template reference extraction with spaces."""
        template = "Hello {{ name }}, welcome to {{  company  }}!"
        
        references = self.validator._extract_template_references(template)
        
        expected = {'name', 'company'}
        assert references == expected
    
    def test_extract_template_references_empty(self):
        """Test template reference extraction with no references."""
        template = "Hello there, welcome to our service!"
        
        references = self.validator._extract_template_references(template)
        
        assert len(references) == 0


def test_validate_campaign_folder_convenience_function():
    """Test the convenience function for campaign validation."""
    temp_dir = tempfile.mkdtemp()
    
    try:
        result = validate_campaign_folder(temp_dir)
        
        assert not result.is_valid
        assert len(result.errors) > 0
        
    finally:
        shutil.rmtree(temp_dir)
