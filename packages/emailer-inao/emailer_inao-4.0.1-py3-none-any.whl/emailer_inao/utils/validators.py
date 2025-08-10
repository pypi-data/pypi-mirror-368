"""
Validation utilities for campaign data and configuration.
"""

import os
import csv
import re
from typing import List, Dict, Set, NamedTuple, Tuple
from email.utils import parseaddr

from .logger import get_logger


class ValidationResult(NamedTuple):
    """Result of a validation operation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class AttachmentValidationResult(NamedTuple):
    """Result of attachment validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    total_size_bytes: int
    attachment_files: List[str]


class CampaignValidator:
    """Validates campaign folder structure and content."""
    
    # Potentially blocked file extensions
    RISKY_EXTENSIONS = {
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar',
        '.zip', '.rar', '.7z', '.tar', '.gz', '.msi', '.deb', '.rpm'
    }
    
    # Email size thresholds in bytes
    SIZE_WARNING_THRESHOLD = 15 * 1024 * 1024  # 15MB
    SIZE_ALARM_THRESHOLD = 20 * 1024 * 1024    # 20MB
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def validate_campaign_folder(self, folder_path: str) -> ValidationResult:
        """Validate complete campaign folder structure and content."""
        errors = []
        warnings = []
        
        # Check required files - now support both .txt and .docx for message files
        required_base_files = ['recipients.csv', 'subject.txt']
        
        for filename in required_base_files:
            file_path = os.path.join(folder_path, filename)
            if not os.path.exists(file_path):
                errors.append(f"Required file missing: {filename}")
            elif not os.path.isfile(file_path):
                errors.append(f"'{filename}' exists but is not a file")
        
        # Check for message file - either msg.txt or msg.docx (but not both)
        msg_txt_path = os.path.join(folder_path, 'msg.txt')
        msg_docx_path = os.path.join(folder_path, 'msg.docx')
        
        msg_txt_exists = os.path.exists(msg_txt_path) and os.path.isfile(msg_txt_path)
        msg_docx_exists = os.path.exists(msg_docx_path) and os.path.isfile(msg_docx_path)
        
        if not msg_txt_exists and not msg_docx_exists:
            errors.append("Message file missing: either msg.txt or msg.docx is required")
        elif msg_txt_exists and msg_docx_exists:
            errors.append("Multiple message files found: only one of msg.txt or msg.docx should exist. Please remove one.")
        
        # If basic files are missing, can't continue validation
        if errors:
            return ValidationResult(False, errors, warnings)
        
        # Validate CSV file
        csv_result = self._validate_csv_file(os.path.join(folder_path, 'recipients.csv'))
        errors.extend(csv_result.errors)
        warnings.extend(csv_result.warnings)
        
        # Validate template files (both .txt and .docx)
        template_result = self._validate_template_files(folder_path)
        errors.extend(template_result.errors)
        warnings.extend(template_result.warnings)
        
        # Validate attachments (if folder exists)
        attachments_folder = os.path.join(folder_path, 'attachments')
        if os.path.exists(attachments_folder):
            attachment_result = self.validate_attachments(attachments_folder)
            errors.extend(attachment_result.errors)
            warnings.extend(attachment_result.warnings)
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)
    
    def validate_attachments(self, attachments_folder: str) -> AttachmentValidationResult:
        """Validate attachments folder and files."""
        errors = []
        warnings = []
        attachment_files = []
        total_size = 0
        
        if not os.path.exists(attachments_folder):
            return AttachmentValidationResult(True, [], [], 0, [])
        
        if not os.path.isdir(attachments_folder):
            errors.append("'attachments' exists but is not a folder")
            return AttachmentValidationResult(False, errors, warnings, 0, [])
        
        # Get all files in attachments folder
        try:
            for filename in os.listdir(attachments_folder):
                file_path = os.path.join(attachments_folder, filename)
                
                # Skip directories
                if os.path.isdir(file_path):
                    continue
                
                # Skip system files (hidden files starting with .)
                if filename.startswith('.'):
                    continue
                
                attachment_files.append(file_path)
                
                # Check file existence and readability
                if not os.path.exists(file_path):
                    errors.append(f"Attachment file not found: {filename}")
                    continue
                
                if not os.access(file_path, os.R_OK):
                    errors.append(f"Cannot read attachment file: {filename}")
                    continue
                
                # Check file type
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in self.RISKY_EXTENSIONS:
                    warnings.append(f"Potentially blocked file type: {filename} ({file_ext})")
                
                # Calculate file size
                try:
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                except OSError as e:
                    errors.append(f"Cannot get size of attachment file {filename}: {e}")
        
        except OSError as e:
            errors.append(f"Cannot read attachments folder: {e}")
            return AttachmentValidationResult(False, errors, warnings, 0, [])
        
        # Validate total email size (including base64 encoding overhead)
        estimated_email_size = self._calculate_estimated_email_size(total_size)
        
        if estimated_email_size > self.SIZE_ALARM_THRESHOLD:
            warnings.append(
                f"🚨 ALARM: Estimated email size {estimated_email_size / (1024*1024):.1f}MB exceeds 20MB\n"
                f"   This may cause delivery failures with most email providers.\n"
                f"   Consider reducing attachment sizes or splitting into multiple emails."
            )
        elif estimated_email_size > self.SIZE_WARNING_THRESHOLD:
            warnings.append(
                f"⚠️  WARNING: Estimated email size {estimated_email_size / (1024*1024):.1f}MB exceeds 15MB\n"
                f"   Email size limits by provider:\n"
                f"   • Gmail: 25MB limit ✓\n"
                f"   • Outlook: 20MB limit ⚠️\n"
                f"   • Yahoo: 25MB limit ✓\n"
                f"   • Many corporate servers: 10-15MB limit ❌\n"
                f"   Consider reducing attachment sizes for better compatibility."
            )
        
        is_valid = len(errors) == 0
        return AttachmentValidationResult(is_valid, errors, warnings, total_size, attachment_files)
    
    def _calculate_estimated_email_size(self, attachment_size_bytes: int) -> int:
        """Calculate estimated email size including base64 encoding overhead."""
        # Base64 encoding increases size by approximately 37%
        # Plus MIME headers and boundaries add additional overhead
        base64_overhead = attachment_size_bytes * 0.37
        mime_overhead = 2048  # Approximate MIME headers and boundaries
        
        # Add some buffer for email content (subject + body)
        content_size = 10240  # 10KB buffer for email content
        
        return int(attachment_size_bytes + base64_overhead + mime_overhead + content_size)
    
    def validate_campaign_folder(self, folder_path: str) -> ValidationResult:
        """Validate complete campaign folder structure and content."""
        errors = []
        warnings = []
        
        # Check required files (except message file which is handled separately)
        required_files = ['recipients.csv', 'subject.txt']
        
        for filename in required_files:
            file_path = os.path.join(folder_path, filename)
            if not os.path.exists(file_path):
                errors.append(f"Required file missing: {filename}")
            elif not os.path.isfile(file_path):
                errors.append(f"'{filename}' exists but is not a file")
        
        # Check for message file - either msg.txt or msg.docx (but not both)
        msg_txt_path = os.path.join(folder_path, 'msg.txt')
        msg_docx_path = os.path.join(folder_path, 'msg.docx')
        
        msg_txt_exists = os.path.exists(msg_txt_path) and os.path.isfile(msg_txt_path)
        msg_docx_exists = os.path.exists(msg_docx_path) and os.path.isfile(msg_docx_path)
        
        if not msg_txt_exists and not msg_docx_exists:
            errors.append("Message file missing: either msg.txt or msg.docx is required")
        elif msg_txt_exists and msg_docx_exists:
            errors.append("Multiple message files found: only one of msg.txt or msg.docx should exist. Please remove one.")
        
        # If basic files are missing, can't continue validation
        if errors:
            return ValidationResult(False, errors, warnings)
        
        # Validate CSV file
        csv_result = self._validate_csv_file(os.path.join(folder_path, 'recipients.csv'))
        errors.extend(csv_result.errors)
        warnings.extend(csv_result.warnings)
        
        # Validate template files
        template_result = self._validate_template_files(folder_path)
        errors.extend(template_result.errors)
        warnings.extend(template_result.warnings)
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)
    
    def _validate_csv_file(self, csv_path: str) -> ValidationResult:
        """Validate recipients CSV file."""
        errors = []
        warnings = []
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                # Check if file is empty
                content = f.read().strip()
                if not content:
                    errors.append("recipients.csv is empty")
                    return ValidationResult(False, errors, warnings)
                
                # Reset file pointer
                f.seek(0)
                
                # Read CSV
                reader = csv.DictReader(f)
                
                # Check if email column exists
                if 'email' not in reader.fieldnames:
                    errors.append("recipients.csv must contain an 'email' column")
                    return ValidationResult(False, errors, warnings)
                
                # Validate data
                emails_seen = set()
                primary_keys_seen = set()
                primary_key_column = reader.fieldnames[0]
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    # Validate email
                    email = row.get('email', '').strip()
                    if not email:
                        errors.append(f"Empty email in row {row_num}")
                    elif not self._is_valid_email(email):
                        errors.append(f"Invalid email '{email}' in row {row_num}")
                    elif email in emails_seen:
                        errors.append(f"Duplicate email '{email}' found in row {row_num}")
                    else:
                        emails_seen.add(email)
                    
                    # Validate primary key (first column)
                    primary_key = row.get(primary_key_column, '').strip()
                    if not primary_key:
                        errors.append(f"Empty primary key '{primary_key_column}' in row {row_num}")
                    elif primary_key in primary_keys_seen:
                        errors.append(f"Duplicate primary key '{primary_key}' in column '{primary_key_column}' at row {row_num}")
                    else:
                        primary_keys_seen.add(primary_key)
                
                # Check if we have any data
                if not emails_seen:
                    errors.append("No valid recipients found in CSV file")
                
        except Exception as e:
            errors.append(f"Error reading recipients.csv: {e}")
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)
    
    def _validate_template_files(self, folder_path: str) -> ValidationResult:
        """Validate template files for placeholder references."""
        errors = []
        warnings = []
        
        try:
            # Load CSV headers to check template references
            csv_path = os.path.join(folder_path, 'recipients.csv')
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                available_fields = set(reader.fieldnames or [])
            
            # Validate template files
            template_files = ['subject.txt']
            
            # Add message template file (either msg.txt or msg.docx)
            msg_txt_path = os.path.join(folder_path, 'msg.txt')
            msg_docx_path = os.path.join(folder_path, 'msg.docx')
            
            if os.path.exists(msg_txt_path):
                template_files.append('msg.txt')
            elif os.path.exists(msg_docx_path):
                template_files.append('msg.docx')
            
            for template_file in template_files:
                template_path = os.path.join(folder_path, template_file)
                
                if template_file.endswith('.docx'):
                    # Handle .docx files using DocumentProcessor
                    from .document_processor import DocumentProcessor
                    doc_processor = DocumentProcessor()
                    
                    try:
                        validation_result = doc_processor.validate_docx_template(
                            template_path, list(available_fields)
                        )
                        
                        if not validation_result.is_valid:
                            errors.extend(validation_result.errors)
                    except Exception as e:
                        errors.append(f"Error validating {template_file}: {e}")
                else:
                    # Handle .txt files
                    with open(template_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find template references using {{field}} pattern
                    template_refs = self._extract_template_references(content)
                    
                    # Check if all references are valid
                    for ref in template_refs:
                        if ref not in available_fields:
                            errors.append(f"Template reference '{{{{{ref}}}}}' in {template_file} not found in CSV columns")
                
        except Exception as e:
            errors.append(f"Error validating template files: {e}")
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email address format."""
        # Use email.utils.parseaddr for basic validation
        parsed = parseaddr(email)
        if not parsed[1]:
            return False
        
        # Additional regex check for common patterns
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, parsed[1]) is not None
    
    def _extract_template_references(self, content: str) -> Set[str]:
        """Extract template references from content using {{field}} pattern."""
        # Find all {{field}} patterns
        pattern = r'\{\{([^}]+)\}\}'
        matches = re.findall(pattern, content)
        return set(match.strip() for match in matches)


# Convenience function for backward compatibility
def validate_campaign_folder(folder_path: str) -> ValidationResult:
    """Validate campaign folder structure and content."""
    validator = CampaignValidator()
    return validator.validate_campaign_folder(folder_path)
