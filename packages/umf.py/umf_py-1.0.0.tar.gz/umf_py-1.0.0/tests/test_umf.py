"""Tests for the UMF Python implementation."""

import unittest
import sys
import os

# Add the src directory to the path so we can import umf
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from umf import parse, Metadata, UMFError


class TestUMFParser(unittest.TestCase):
    """Test cases for UMF parsing functionality."""

    def test_basic_parsing(self):
        """Test basic UMF parsing."""
        source = """UMF Python Parser

[ Github ]
Author: IceBrick
Language: Python"""

        metadata = parse(source)
        
        self.assertEqual(metadata.media_name, "UMF Python Parser")
        self.assertEqual(metadata.get('Github', 'Author'), 'IceBrick')
        self.assertEqual(metadata.get('Github', 'Language'), 'Python')

    def test_global_fields(self):
        """Test parsing global fields."""
        source = """Test Media
Version: 1.0.0
Type: Test"""

        metadata = parse(source)
        
        self.assertEqual(metadata.media_name, "Test Media")
        self.assertEqual(metadata.get(None, 'Version'), '1.0.0')
        self.assertEqual(metadata.get(None, 'Type'), 'Test')

    def test_mixed_fields(self):
        """Test parsing mixed global and grouped fields."""
        source = """Mixed Media
GlobalField: GlobalValue

[ Group1 ]
Field1: Value1
Field2: Value2

[ Group2 ]
Field3: Value3"""

        metadata = parse(source)
        
        self.assertEqual(metadata.media_name, "Mixed Media")
        self.assertEqual(metadata.get(None, 'GlobalField'), 'GlobalValue')
        self.assertEqual(metadata.get('Group1', 'Field1'), 'Value1')
        self.assertEqual(metadata.get('Group1', 'Field2'), 'Value2')
        self.assertEqual(metadata.get('Group2', 'Field3'), 'Value3')

    def test_fallback_to_global(self):
        """Test that grouped fields fall back to global fields."""
        source = """Fallback Test
GlobalField: GlobalValue

[ Group ]
LocalField: LocalValue"""

        metadata = parse(source)
        
        # Should find local field in group
        self.assertEqual(metadata.get('Group', 'LocalField'), 'LocalValue')
        # Should fall back to global field
        self.assertEqual(metadata.get('Group', 'GlobalField'), 'GlobalValue')
        # Should not find non-existent field
        self.assertIsNone(metadata.get('Group', 'NonExistent'))

    def test_comments_and_empty_lines(self):
        """Test that comments and empty lines are ignored."""
        source = """Test Media

# This is a comment
Version: 1.0.0

# Another comment
[ Group ]
# Comment in group
Field: Value

"""

        metadata = parse(source)
        
        self.assertEqual(metadata.media_name, "Test Media")
        self.assertEqual(metadata.get(None, 'Version'), '1.0.0')
        self.assertEqual(metadata.get('Group', 'Field'), 'Value')

    def test_has_method(self):
        """Test the has method."""
        source = """Test Media
ExistingField: Value

[ Group ]
GroupField: GroupValue"""

        metadata = parse(source)
        
        self.assertTrue(metadata.has(None, 'ExistingField'))
        self.assertFalse(metadata.has(None, 'NonExistentField'))
        self.assertTrue(metadata.has('Group', 'GroupField'))
        self.assertTrue(metadata.has('Group', 'ExistingField'))  # Falls back to global
        self.assertFalse(metadata.has('Group', 'NonExistentField'))

    def test_set_method(self):
        """Test the set method."""
        metadata = Metadata("Test Media")
        
        metadata.set(None, 'GlobalField', 'GlobalValue')
        metadata.set('Group', 'GroupField', 'GroupValue')
        
        self.assertEqual(metadata.get(None, 'GlobalField'), 'GlobalValue')
        self.assertEqual(metadata.get('Group', 'GroupField'), 'GroupValue')

    def test_string_representation(self):
        """Test the string representation."""
        metadata = Metadata("Test Media")
        metadata.set(None, 'GlobalField', 'GlobalValue')
        metadata.set('Group', 'GroupField', 'GroupValue')
        
        result = str(metadata)
        expected = """Test Media

GlobalField: GlobalValue

[ Group ]

GroupField: GroupValue"""
        
        self.assertEqual(result, expected)

    def test_error_empty_media_name(self):
        """Test error handling for empty media name."""
        with self.assertRaises(UMFError) as cm:
            parse("")
        
        self.assertIn("Empty Media Name", str(cm.exception))

    def test_error_empty_header_name(self):
        """Test error handling for empty header name."""
        source = """Test Media
[ ]"""
        
        with self.assertRaises(UMFError) as cm:
            parse(source)
        
        self.assertIn("Empty Header Name", str(cm.exception))

    def test_error_empty_field_name(self):
        """Test error handling for empty field name."""
        source = """Test Media
: Value"""
        
        with self.assertRaises(UMFError) as cm:
            parse(source)
        
        self.assertIn("Empty Field Name", str(cm.exception))

    def test_error_empty_field_value(self):
        """Test error handling for empty field value."""
        source = """Test Media
FieldName:"""
        
        with self.assertRaises(UMFError) as cm:
            parse(source)
        
        self.assertIn("Empty Field Value", str(cm.exception))

    def test_error_invalid_line(self):
        """Test error handling for invalid line format."""
        source = """Test Media
This is not a valid line"""
        
        with self.assertRaises(UMFError) as cm:
            parse(source)
        
        self.assertIn("Invalid Line", str(cm.exception))


if __name__ == '__main__':
    unittest.main()
