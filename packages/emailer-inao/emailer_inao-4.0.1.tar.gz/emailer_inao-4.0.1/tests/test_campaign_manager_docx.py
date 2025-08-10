"""
Tests for campaign manager .docx message file support in config show.
"""

import os
import tempfile
import shutil
from unittest.mock import patch
from docx import Document

from src.emailer_inao.core.campaign_manager import CampaignManager


class TestCampaignManagerDocx:
    """Test cases for CampaignManager .docx support."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.campaign_manager = CampaignManager()
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_campaign_with_docx(self):
        """Create a valid campaign folder with .docx message file."""
        # Create recipients.csv
        recipients_content = """email,name,company
john@example.com,John Doe,ACME Corp
jane@example.com,Jane Smith,Tech Inc"""
        
        with open(os.path.join(self.temp_dir, 'recipients.csv'), 'w') as f:
            f.write(recipients_content)
        
        # Create subject.txt
        with open(os.path.join(self.temp_dir, 'subject.txt'), 'w') as f:
            f.write("Welcome {{name}}!")
        
        # Create msg.docx
        doc = Document()
        doc.add_paragraph("Hello {{name}}, welcome to {{company}}!")
        doc.save(os.path.join(self.temp_dir, 'msg.docx'))
    
    def test_config_show_recognizes_docx_message_file(self, capsys):
        """Test that config show recognizes .docx message files."""
        self.create_campaign_with_docx()
        
        # Load campaign
        result = self.campaign_manager.create_or_load_campaign(self.temp_dir)
        assert result == 0
        
        # Show configuration
        result = self.campaign_manager.show_configuration()
        assert result == 0
        
        # Check output
        captured = capsys.readouterr()
        assert "Message file: ✅ msg.docx" in captured.out
        assert "Message file: ❌" not in captured.out
    
    def test_config_show_recognizes_txt_message_file(self, capsys):
        """Test that config show still recognizes .txt message files."""
        # Create campaign with .txt file
        recipients_content = """email,name,company
john@example.com,John Doe,ACME Corp"""
        
        with open(os.path.join(self.temp_dir, 'recipients.csv'), 'w') as f:
            f.write(recipients_content)
        
        with open(os.path.join(self.temp_dir, 'subject.txt'), 'w') as f:
            f.write("Welcome {{name}}!")
        
        with open(os.path.join(self.temp_dir, 'msg.txt'), 'w') as f:
            f.write("Hello {{name}}, welcome to {{company}}!")
        
        # Load campaign
        result = self.campaign_manager.create_or_load_campaign(self.temp_dir)
        assert result == 0
        
        # Show configuration
        result = self.campaign_manager.show_configuration()
        assert result == 0
        
        # Check output
        captured = capsys.readouterr()
        assert "Message file: ✅ msg.txt" in captured.out
        assert "Message file: ❌" not in captured.out
    
    def test_config_show_warns_about_both_message_files(self, capsys):
        """Test that config show warns when both .txt and .docx exist."""
        self.create_campaign_with_docx()
        
        # Add msg.txt as well
        with open(os.path.join(self.temp_dir, 'msg.txt'), 'w') as f:
            f.write("Hello {{name}}!")
        
        # Try to load campaign (should fail)
        result = self.campaign_manager.create_or_load_campaign(self.temp_dir)
        assert result == 1  # Should fail due to validation
        
        # Check that validation caught the issue
        captured = capsys.readouterr()
        assert "Multiple message files found" in captured.out
    
    def test_config_show_no_message_file(self, capsys):
        """Test that config show shows ❌ when no message file exists."""
        # Create campaign without message file
        recipients_content = """email,name,company
john@example.com,John Doe,ACME Corp"""
        
        with open(os.path.join(self.temp_dir, 'recipients.csv'), 'w') as f:
            f.write(recipients_content)
        
        with open(os.path.join(self.temp_dir, 'subject.txt'), 'w') as f:
            f.write("Welcome {{name}}!")
        
        # Try to load campaign (should fail)
        result = self.campaign_manager.create_or_load_campaign(self.temp_dir)
        assert result == 1  # Should fail due to missing message file
        
        # Check that validation caught the issue
        captured = capsys.readouterr()
        assert "Message file missing" in captured.out
