import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'dream_layer_backend'))

from txt2img_workflow import parse_prompts_from_file_content

class TestBatchPrompts(unittest.TestCase):
    
    def test_parse_prompts_from_file_content(self):
        """Test parsing prompts from file content"""
        file_content = """# Test batch prompts
a beautiful sunset over mountains
a steampunk flying machine
# This line will be skipped

a cyberpunk city at night
a magical forest with glowing mushrooms"""
        
        expected_prompts = [
            "a beautiful sunset over mountains",
            "a steampunk flying machine", 
            "a cyberpunk city at night",
            "a magical forest with glowing mushrooms"
        ]
        
        result = parse_prompts_from_file_content(file_content)
        self.assertEqual(result, expected_prompts)
    
    def test_parse_empty_file(self):
        """Test parsing empty file content"""
        result = parse_prompts_from_file_content("")
        self.assertEqual(result, [])
    
    def test_parse_only_comments(self):
        """Test parsing file with only comments"""
        file_content = """# Comment 1
# Comment 2
# Comment 3"""
        result = parse_prompts_from_file_content(file_content)
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()
