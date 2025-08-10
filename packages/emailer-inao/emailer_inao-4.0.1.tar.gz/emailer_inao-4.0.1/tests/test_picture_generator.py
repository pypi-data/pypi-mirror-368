"""
Tests for picture generator functionality.
"""

import os
import tempfile
import shutil
import pytest
from unittest.mock import patch, MagicMock
from PIL import Image

from emailer_inao.core.picture_generator import PictureGenerator, PictureGeneratorProject


class TestPictureGeneratorProject:
    """Test cases for PictureGeneratorProject class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = os.path.join(self.temp_dir, 'test-project')
        os.makedirs(self.project_path)
        self.project = PictureGeneratorProject(self.project_path, 'test-project')
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_test_template(self):
        """Create a test JPEG template."""
        # Create a simple test image
        img = Image.new('RGB', (400, 300), color='white')
        img.save(self.project.template_file, 'JPEG')
    
    def create_test_fusion_csv(self, content=None):
        """Create a test fusion CSV file."""
        if content is None:
            content = """fusion-type,data,positioning,size,alignment
text,"Test Event",200:50,24,center
graphic,logo.png,50:50,100:,left"""
        
        with open(self.project.fusion_file, 'w') as f:
            f.write(content)
    
    def test_exists_true(self):
        """Test exists method when project folder exists."""
        assert self.project.exists()
    
    def test_exists_false(self):
        """Test exists method when project folder doesn't exist."""
        shutil.rmtree(self.project_path)
        assert not self.project.exists()
    
    def test_should_attach_to_email_true(self):
        """Test should_attach_to_email when attach.txt contains 'true'."""
        with open(self.project.attach_file, 'w') as f:
            f.write('true')
        
        assert self.project.should_attach_to_email()
    
    def test_should_attach_to_email_false(self):
        """Test should_attach_to_email when attach.txt contains 'false'."""
        with open(self.project.attach_file, 'w') as f:
            f.write('false')
        
        assert not self.project.should_attach_to_email()
    
    def test_should_attach_to_email_missing_file(self):
        """Test should_attach_to_email when attach.txt doesn't exist."""
        assert not self.project.should_attach_to_email()
    
    def test_is_valid_missing_template(self):
        """Test validation when template.jpg is missing."""
        self.create_test_fusion_csv()
        
        result = self.project.is_valid()
        
        assert not result.is_valid
        assert any('Template file missing' in error for error in result.errors)
    
    def test_is_valid_missing_fusion_csv(self):
        """Test validation when fusion.csv is missing."""
        self.create_test_template()
        
        result = self.project.is_valid()
        
        assert not result.is_valid
        assert any('Fusion file missing' in error for error in result.errors)
    
    def test_is_valid_success(self):
        """Test successful validation."""
        self.create_test_template()
        self.create_test_fusion_csv()
        
        result = self.project.is_valid()
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_fusion_csv_missing_columns(self):
        """Test fusion CSV validation with missing required columns."""
        self.create_test_template()
        
        # Create CSV with missing columns
        with open(self.project.fusion_file, 'w') as f:
            f.write("fusion-type,data\ntext,Hello")
        
        result = self.project.is_valid()
        
        assert not result.is_valid
        assert any('Missing required columns' in error for error in result.errors)
    
    def test_validate_fusion_csv_invalid_fusion_type(self):
        """Test fusion CSV validation with invalid fusion-type."""
        self.create_test_template()
        
        content = """fusion-type,data,positioning,size,alignment
invalid,Hello,100:100,24,center"""
        self.create_test_fusion_csv(content)
        
        result = self.project.is_valid()
        
        assert not result.is_valid
        assert any('fusion-type must be' in error for error in result.errors)
    
    def test_validate_fusion_csv_invalid_positioning(self):
        """Test fusion CSV validation with invalid positioning format."""
        self.create_test_template()
        
        content = """fusion-type,data,positioning,size,alignment
text,Hello,invalid,24,center"""
        self.create_test_fusion_csv(content)
        
        result = self.project.is_valid()
        
        assert not result.is_valid
        assert any('positioning must be in format' in error for error in result.errors)
    
    def test_validate_fusion_csv_invalid_text_size(self):
        """Test fusion CSV validation with invalid text size."""
        self.create_test_template()
        
        content = """fusion-type,data,positioning,size,alignment
text,Hello,100:100,invalid,center"""
        self.create_test_fusion_csv(content)
        
        result = self.project.is_valid()
        
        assert not result.is_valid
        assert any('size for text must be a number' in error for error in result.errors)
    
    def test_validate_fusion_csv_invalid_graphic_size(self):
        """Test fusion CSV validation with invalid graphic size."""
        self.create_test_template()
        
        content = """fusion-type,data,positioning,size,alignment
graphic,logo.png,100:100,invalid,center"""
        self.create_test_fusion_csv(content)
        
        result = self.project.is_valid()
        
        assert not result.is_valid
        assert any('size for graphic must be' in error for error in result.errors)
    
    def test_validate_fusion_csv_invalid_alignment(self):
        """Test fusion CSV validation with invalid alignment."""
        self.create_test_template()
        
        content = """fusion-type,data,positioning,size,alignment
text,Hello,100:100,24,invalid"""
        self.create_test_fusion_csv(content)
        
        result = self.project.is_valid()
        
        assert not result.is_valid
        assert any('alignment must be' in error for error in result.errors)
    
    def test_validate_fusion_csv_invalid_orientation(self):
        """Test fusion CSV validation with invalid orientation."""
        self.create_test_template()
        
        content = """fusion-type,data,positioning,size,alignment,orientation
text,Hello,100:100,24,center,200"""
        self.create_test_fusion_csv(content)
        
        result = self.project.is_valid()
        
        assert not result.is_valid
        assert any('orientation must be between -180 and 180' in error for error in result.errors)


class TestPictureGenerator:
    """Test cases for PictureGenerator class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = PictureGenerator(self.temp_dir)
        self.pg_folder = os.path.join(self.temp_dir, 'picture-generator')
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_test_project(self, project_name='test-project'):
        """Create a test project with valid files."""
        project_path = os.path.join(self.pg_folder, project_name)
        os.makedirs(project_path, exist_ok=True)
        
        # Create template
        img = Image.new('RGB', (400, 300), color='white')
        template_file = os.path.join(project_path, 'template.jpg')
        img.save(template_file, 'JPEG')
        
        # Create fusion CSV
        fusion_content = """fusion-type,data,positioning,size,alignment
text,"{{name}}",200:100,24,center
text,"{{company}}",200:150,18,center"""
        
        fusion_file = os.path.join(project_path, 'fusion.csv')
        with open(fusion_file, 'w') as f:
            f.write(fusion_content)
        
        # Create attach.txt
        attach_file = os.path.join(project_path, 'attach.txt')
        with open(attach_file, 'w') as f:
            f.write('true')
        
        return project_path
    
    def test_get_projects_empty(self):
        """Test get_projects when no projects exist."""
        projects = self.generator.get_projects()
        assert len(projects) == 0
    
    def test_get_projects_with_projects(self):
        """Test get_projects with existing projects."""
        self.create_test_project('project1')
        self.create_test_project('project2')
        
        projects = self.generator.get_projects()
        
        assert len(projects) == 2
        project_names = [p.project_name for p in projects]
        assert 'project1' in project_names
        assert 'project2' in project_names
    
    def test_validate_projects_success(self):
        """Test successful project validation with generated data."""
        project_path = self.create_test_project()
        recipients = [{'id': '001', 'name': 'John', 'company': 'ACME'}]
        
        # Create data folder and matching generated file
        project = PictureGeneratorProject(project_path, 'test-project')
        os.makedirs(project.data_folder, exist_ok=True)
        with open(os.path.join(project.data_folder, '001.jpg'), 'w') as f:
            f.write('test image data')
        
        result = self.generator.validate_projects(recipients)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_projects_invalid_project(self):
        """Test project validation with invalid project."""
        # Create project without template
        project_path = os.path.join(self.pg_folder, 'invalid-project')
        os.makedirs(project_path, exist_ok=True)
        
        recipients = [{'id': '001', 'name': 'John'}]
        
        result = self.generator.validate_projects(recipients)
        
        assert not result.is_valid
        assert len(result.errors) > 0
    
    def test_check_data_consistency_no_data_folder(self):
        """Test data consistency check when no data folder exists."""
        project_path = self.create_test_project()
        project = PictureGeneratorProject(project_path, 'test-project')
        recipients = [{'id': '001', 'name': 'John'}]
        
        result = self.generator._check_data_consistency(project, recipients)
        
        assert not result.is_valid  # Changed: now expects error, not warning
        assert any('No generated data found' in error for error in result.errors)
        assert 'emailer-inao picture generate' in ' '.join(result.errors)  # Check guidance is provided
    
    def test_check_data_consistency_missing_files(self):
        """Test data consistency check with missing generated files."""
        project_path = self.create_test_project()
        project = PictureGeneratorProject(project_path, 'test-project')
        
        # Create data folder but no files
        os.makedirs(project.data_folder)
        
        recipients = [{'id': '001', 'name': 'John'}, {'id': '002', 'name': 'Jane'}]
        
        result = self.generator._check_data_consistency(project, recipients)
        
        assert not result.is_valid  # Changed: now expects error, not warning
        assert any('Missing generated files for recipients' in error for error in result.errors)
        assert any('out of sync' in error for error in result.errors)  # Check sync guidance
    
    def test_check_data_consistency_extra_files(self):
        """Test data consistency check with extra generated files."""
        project_path = self.create_test_project()
        project = PictureGeneratorProject(project_path, 'test-project')
        
        # Create data folder with extra files
        os.makedirs(project.data_folder)
        with open(os.path.join(project.data_folder, '001.jpg'), 'w') as f:
            f.write('test')
        with open(os.path.join(project.data_folder, '999.jpg'), 'w') as f:
            f.write('extra')
        
        recipients = [{'id': '001', 'name': 'John'}]
        
        result = self.generator._check_data_consistency(project, recipients)
        
        assert not result.is_valid  # Changed: now expects error, not warning
        assert any('Found generated files for recipients not in current list' in error for error in result.errors)
        assert any('out of sync' in error for error in result.errors)  # Check sync guidance
    
    @patch('emailer_inao.core.picture_generator.PictureGenerator._generate_single_picture')
    def test_generate_pictures_success(self, mock_generate):
        """Test successful picture generation."""
        self.create_test_project()
        recipients = [
            {'id': '001', 'name': 'John', 'company': 'ACME'},
            {'id': '002', 'name': 'Jane', 'company': 'TechCorp'}
        ]
        
        result = self.generator.generate_pictures('test-project', recipients)
        
        assert result == 0
        assert mock_generate.call_count == 2
    
    def test_generate_pictures_project_not_found(self):
        """Test picture generation with non-existent project."""
        recipients = [{'id': '001', 'name': 'John'}]
        
        result = self.generator.generate_pictures('nonexistent', recipients)
        
        assert result == 1
    
    def test_generate_pictures_email_primary_key(self):
        """Test picture generation with email as primary key (should fail)."""
        self.create_test_project()
        recipients = [{'email': 'john@example.com', 'name': 'John'}]
        
        result = self.generator.generate_pictures('test-project', recipients)
        
        assert result == 1
    
    def test_generate_pictures_no_recipients(self):
        """Test picture generation with no recipients."""
        self.create_test_project()
        recipients = []
        
        result = self.generator.generate_pictures('test-project', recipients)
        
        assert result == 1
    
    def test_load_fusion_instructions(self):
        """Test loading fusion instructions from CSV."""
        project_path = self.create_test_project()
        fusion_file = os.path.join(project_path, 'fusion.csv')
        
        instructions = self.generator._load_fusion_instructions(fusion_file)
        
        assert len(instructions) == 2
        assert instructions[0]['fusion-type'] == 'text'
        assert instructions[0]['data'] == '{{name}}'
    
    def test_parse_color_hex(self):
        """Test color parsing with hex values."""
        color = self.generator._parse_color('#FF0000')
        assert color == '#ff0000'  # Implementation converts to lowercase
    
    def test_parse_color_named(self):
        """Test color parsing with named colors."""
        color = self.generator._parse_color('red')
        assert color == '#FF0000'
        
        color = self.generator._parse_color('black')
        assert color == '#000000'
    
    def test_parse_color_unknown(self):
        """Test color parsing with unknown color name."""
        color = self.generator._parse_color('unknown')
        assert color == '#000000'  # Should default to black
    
    def test_resize_graphic_both_dimensions(self):
        """Test graphic resizing with both width and height specified."""
        img = Image.new('RGB', (200, 100), color='white')
        
        resized = self.generator._resize_graphic(img, '400:200')
        
        assert resized.size == (400, 200)
    
    def test_resize_graphic_width_only(self):
        """Test graphic resizing with only width specified."""
        img = Image.new('RGB', (200, 100), color='white')
        
        resized = self.generator._resize_graphic(img, '400:')
        
        assert resized.size == (400, 200)  # Maintains aspect ratio
    
    def test_resize_graphic_height_only(self):
        """Test graphic resizing with only height specified."""
        img = Image.new('RGB', (200, 100), color='white')
        
        resized = self.generator._resize_graphic(img, ':200')
        
        assert resized.size == (400, 200)  # Maintains aspect ratio
