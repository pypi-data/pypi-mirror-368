"""
Tests for campaign manager functionality.
"""

import os
import tempfile
import shutil
import pytest
from unittest.mock import patch, MagicMock

from emailer_inao.core.campaign_manager import CampaignManager
from emailer_inao.utils.validators import ValidationResult


class TestCampaignManager:
    """Test cases for CampaignManager class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.campaign_manager = CampaignManager()
        # Clear any existing active campaign for test isolation
        self.campaign_manager.active_campaign_folder = None
        self.campaign_manager.credential_manager = None
        self.campaign_manager.picture_generator = None
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_valid_campaign_folder(self):
        """Create a valid campaign folder for testing."""
        # Create recipients.csv
        recipients_content = """email,name,company
john@example.com,John Doe,ACME Corp
jane@example.com,Jane Smith,Tech Inc"""
        
        with open(os.path.join(self.temp_dir, 'recipients.csv'), 'w') as f:
            f.write(recipients_content)
        
        # Create msg.txt
        msg_content = "Dear {{name}},\n\nWelcome to {{company}}!\n\nBest regards"
        with open(os.path.join(self.temp_dir, 'msg.txt'), 'w') as f:
            f.write(msg_content)
        
        # Create subject.txt
        subject_content = "Welcome {{name}} to our service"
        with open(os.path.join(self.temp_dir, 'subject.txt'), 'w') as f:
            f.write(subject_content)
    
    def test_create_campaign_nonexistent_folder(self):
        """Test creating campaign with non-existent folder."""
        nonexistent_path = os.path.join(self.temp_dir, 'nonexistent')
        result = self.campaign_manager.create_or_load_campaign(nonexistent_path)
        
        assert result == 1
        assert not self.campaign_manager.has_active_campaign()
    
    @patch('emailer_inao.utils.validators.validate_campaign_folder')
    def test_create_campaign_validation_failure(self, mock_validate):
        """Test creating campaign with validation failure."""
        mock_validate.return_value = ValidationResult(
            is_valid=False,
            errors=['Missing recipients.csv'],
            warnings=[]
        )
        
        result = self.campaign_manager.create_or_load_campaign(self.temp_dir)
        
        assert result == 1
        assert not self.campaign_manager.has_active_campaign()
    
    @patch('emailer_inao.utils.validators.validate_campaign_folder')
    @patch('builtins.input', return_value='n')
    def test_create_campaign_warnings_declined(self, mock_input, mock_validate):
        """Test creating campaign with warnings that user declines."""
        mock_validate.return_value = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=['Some warning']
        )
        
        result = self.campaign_manager.create_or_load_campaign(self.temp_dir)
        
        assert result == 1
        assert not self.campaign_manager.has_active_campaign()
    
    @patch('emailer_inao.core.campaign_manager.validate_campaign_folder')
    @patch('builtins.input', return_value='y')
    def test_create_campaign_warnings_accepted(self, mock_input, mock_validate):
        """Test creating campaign with warnings that user accepts."""
        mock_validate.return_value = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=['Some warning']
        )
        
        result = self.campaign_manager.create_or_load_campaign(self.temp_dir)
        
        assert result == 0
        assert self.campaign_manager.has_active_campaign()
        assert self.campaign_manager.get_active_campaign() == self.temp_dir
    
    @patch('emailer_inao.core.campaign_manager.validate_campaign_folder')
    def test_create_campaign_success(self, mock_validate):
        """Test successful campaign creation."""
        mock_validate.return_value = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[]
        )
        
        result = self.campaign_manager.create_or_load_campaign(self.temp_dir)
        
        assert result == 0
        assert self.campaign_manager.has_active_campaign()
        assert self.campaign_manager.get_active_campaign() == self.temp_dir
        
        # Check that directories were created
        assert os.path.exists(os.path.join(self.temp_dir, 'logs'))
        assert os.path.exists(os.path.join(self.temp_dir, 'dryrun'))
    
    def test_configure_smtp_no_active_campaign(self):
        """Test SMTP configuration without active campaign."""
        result = self.campaign_manager.configure_smtp()
        
        assert result == 1
    
    @patch('emailer_inao.core.campaign_manager.validate_campaign_folder')
    @patch('builtins.input')
    @patch('getpass.getpass')
    @patch('emailer_inao.utils.smtp_helper.SMTPHelper.test_connection')
    def test_configure_smtp_success(self, mock_test_conn, mock_getpass, mock_input, mock_validate):
        """Test successful SMTP configuration."""
        # Setup campaign first
        mock_validate.return_value = ValidationResult(True, [], [])
        self.campaign_manager.create_or_load_campaign(self.temp_dir)
        
        # Mock user inputs
        mock_input.side_effect = ['smtp.gmail.com', '587', 'user@gmail.com', '1']
        mock_getpass.return_value = 'password123'
        mock_test_conn.return_value = True
        
        result = self.campaign_manager.configure_smtp()
        
        assert result == 0
    
    @patch('emailer_inao.utils.validators.validate_campaign_folder')
    @patch('builtins.input')
    @patch('getpass.getpass')
    @patch('emailer_inao.utils.smtp_helper.SMTPHelper.test_connection')
    def test_configure_smtp_test_failure_declined(self, mock_test_conn, mock_getpass, mock_input, mock_validate):
        """Test SMTP configuration with test failure that user declines to save."""
        # Setup campaign first
        mock_validate.return_value = ValidationResult(True, [], [])
        self.campaign_manager.create_or_load_campaign(self.temp_dir)
        
        # Mock user inputs
        mock_input.side_effect = ['smtp.gmail.com', '587', 'user@gmail.com', '1', 'n']
        mock_getpass.return_value = 'password123'
        mock_test_conn.return_value = False
        
        result = self.campaign_manager.configure_smtp()
        
        assert result == 1
    
    def test_show_configuration_no_active_campaign(self):
        """Test showing configuration without active campaign."""
        result = self.campaign_manager.show_configuration()
        
        assert result == 1
    
    @patch('emailer_inao.core.campaign_manager.validate_campaign_folder')
    def test_show_configuration_success(self, mock_validate):
        """Test successful configuration display."""
        mock_validate.return_value = ValidationResult(True, [], [])
        self.campaign_manager.create_or_load_campaign(self.temp_dir)
        
        # Create some files to test status
        self.create_valid_campaign_folder()
        
        result = self.campaign_manager.show_configuration()
        
        assert result == 0
    
    def test_has_active_campaign_false(self):
        """Test has_active_campaign when no campaign is loaded."""
        assert not self.campaign_manager.has_active_campaign()
    
    @patch('emailer_inao.core.campaign_manager.validate_campaign_folder')
    def test_has_active_campaign_true(self, mock_validate):
        """Test has_active_campaign when campaign is loaded."""
        mock_validate.return_value = ValidationResult(True, [], [])
        self.campaign_manager.create_or_load_campaign(self.temp_dir)
        
        assert self.campaign_manager.has_active_campaign()
    
    def test_get_active_campaign_none(self):
        """Test get_active_campaign when no campaign is loaded."""
        assert self.campaign_manager.get_active_campaign() is None
    
    @patch('emailer_inao.core.campaign_manager.validate_campaign_folder')
    def test_get_active_campaign_path(self, mock_validate):
        """Test get_active_campaign returns correct path."""
        mock_validate.return_value = ValidationResult(True, [], [])
        self.campaign_manager.create_or_load_campaign(self.temp_dir)
        
        assert self.campaign_manager.get_active_campaign() == self.temp_dir
