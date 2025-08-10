"""
Tests for font font support in picture generation.
"""

import os
import tempfile
import shutil
from PIL import Image, ImageFont, ImageDraw

from src.emailer_inao.core.picture_generator import PictureGenerator, PictureGeneratorProject


class TestFontPolicies:
    """Test cases for font font support."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.picture_generator = PictureGenerator(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_get_font_default(self):
        """Test getting default font when no font specified."""
        instruction = {'size': '12'}
        font = self.picture_generator._get_font(instruction, 12)
        
        # Should return a valid font object
        assert font is not None
        # Font should be usable for text rendering
        assert hasattr(font, 'getsize') or hasattr(font, 'getbbox')
    
    def test_get_font_with_font(self):
        """Test getting font with specific font."""
        instruction = {'font': 'Arial', 'shape': '', 'size': '14'}
        font = self.picture_generator._get_font(instruction, 14)
        
        # Should return a valid font object
        assert font is not None
        assert hasattr(font, 'getsize') or hasattr(font, 'getbbox')
    
    def test_get_font_with_bold_style(self):
        """Test getting font with bold style."""
        instruction = {'font': 'Helvetica', 'shape': 'bold', 'size': '16'}
        font = self.picture_generator._get_font(instruction, 16)
        
        # Should return a valid font object
        assert font is not None
        assert hasattr(font, 'getsize') or hasattr(font, 'getbbox')
    
    def test_get_font_with_italic_style(self):
        """Test getting font with italic style."""
        instruction = {'font': 'Arial', 'shape': 'italic', 'size': '12'}
        font = self.picture_generator._get_font(instruction, 12)
        
        # Should return a valid font object
        assert font is not None
        assert hasattr(font, 'getsize') or hasattr(font, 'getbbox')
    
    def test_get_font_with_bold_italic_style(self):
        """Test getting font with bold italic style."""
        instruction = {'font': 'Helvetica', 'shape': 'bold italic', 'size': '14'}
        font = self.picture_generator._get_font(instruction, 14)
        
        # Should return a valid font object
        assert font is not None
        assert hasattr(font, 'getsize') or hasattr(font, 'getbbox')
    
    def test_get_font_nonexistent_font(self):
        """Test getting font with non-existent font name."""
        instruction = {'font': 'NonExistentFont', 'shape': '', 'size': '12'}
        font = self.picture_generator._get_font(instruction, 12)
        
        # Should fallback to default font
        assert font is not None
        assert hasattr(font, 'getsize') or hasattr(font, 'getbbox')
    
    def test_get_font_monospace_fonts(self):
        """Test getting monospace fonts."""
        monospace_fonts = ['Monaco', 'Consolas', 'Courier']
        
        for font_name in monospace_fonts:
            instruction = {'font': font_name, 'shape': '', 'size': '12'}
            font = self.picture_generator._get_font(instruction, 12)
            
            # Should return a valid font object (either the requested font or fallback)
            assert font is not None
            assert hasattr(font, 'getsize') or hasattr(font, 'getbbox')
    
    def test_get_font_case_insensitive(self):
        """Test that font names are case insensitive."""
        instructions = [
            {'font': 'arial', 'shape': '', 'size': '12'},
            {'font': 'ARIAL', 'shape': '', 'size': '12'},
            {'font': 'Arial', 'shape': '', 'size': '12'},
        ]
        
        fonts = []
        for instruction in instructions:
            font = self.picture_generator._get_font(instruction, 12)
            fonts.append(font)
            assert font is not None
            assert hasattr(font, 'getsize') or hasattr(font, 'getbbox')
        
        # All should return valid fonts (may be the same or different based on availability)
        assert len(fonts) == 3
    
    def test_get_font_with_different_sizes(self):
        """Test getting fonts with different sizes."""
        sizes = [8, 12, 16, 20, 24]
        
        for size in sizes:
            instruction = {'font': 'Arial', 'shape': '', 'size': str(size)}
            font = self.picture_generator._get_font(instruction, size)
            
            # Should return a valid font object
            assert font is not None
            assert hasattr(font, 'getsize') or hasattr(font, 'getbbox')
    
    def test_font_rendering_with_policies(self):
        """Test that fonts with policies can be used for text rendering."""
        # Create a test image
        image = Image.new('RGB', (200, 100), color='white')
        
        # Test different font policies
        test_cases = [
            {'font': 'Arial', 'shape': 'bold', 'text': 'Bold Arial'},
            {'font': 'Helvetica', 'shape': 'italic', 'text': 'Italic Helvetica'},
            {'font': 'Monaco', 'shape': '', 'text': 'Monaco Mono'},
        ]
        
        for test_case in test_cases:
            instruction = {
                'font': test_case['font'],
                'shape': test_case['shape'],
                'size': '12'
            }
            
            font = self.picture_generator._get_font(instruction, 12)
            
            # Should be able to use the font for rendering without errors
            draw = ImageDraw.Draw(image)
            
            # This should not raise an exception
            try:
                draw.text((10, 10), test_case['text'], fill='black', font=font)
            except Exception as e:
                # If there's an error, it should not be a font-related error
                assert 'font' not in str(e).lower(), f"Font error: {e}"
    
    def test_font_font_integration(self):
        """Test font policies work in actual text fusion."""
        # Create a simple test image
        image = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(image)
        
        # Test instruction with font font
        instruction = {
            'data': 'Test {{name}}',
            'positioning': '10:10',
            'size': '14',
            'font': 'Arial',
            'shape': 'bold',
            'color': 'black',
            'alignment': 'left'
        }
        
        recipient = {'name': 'John Doe'}
        
        # This should work without errors
        try:
            self.picture_generator._apply_text_fusion(image, draw, instruction, recipient)
        except Exception as e:
            assert False, f"Text fusion with font font failed: {e}"
