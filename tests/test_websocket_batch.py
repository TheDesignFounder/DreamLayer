import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'dream_layer_backend'))

from txt2img_workflow import parse_prompts_from_file_content

class TestWebSocketBatch(unittest.TestCase):
    
    def test_batch_prompts_parsing(self):
        """Test that batch prompts are parsed correctly for WebSocket processing"""
        test_file_path = os.path.join(os.path.dirname(__file__), 'test_batch_prompts.txt')
        
        with open(test_file_path, 'r') as f:
            content = f.read()
        
        prompts = parse_prompts_from_file_content(content)
        
        expected_prompts = [
            "a beautiful sunset over mountains",
            "a steampunk flying machine",
            "a cyberpunk city at night", 
            "a magical forest with glowing mushrooms",
            "a vintage car on a desert road"
        ]
        
        self.assertEqual(prompts, expected_prompts)
        self.assertEqual(len(prompts), 5)
    
    def test_websocket_message_format(self):
        """Test WebSocket message format structure"""
        progress_message = {
            'type': 'progress',
            'current': 3,
            'total': 10,
            'current_prompt': 'a beautiful sunset over mountains',
            'status': 'processing'
        }
        
        # Verify required fields
        self.assertIn('type', progress_message)
        self.assertIn('current', progress_message)
        self.assertIn('total', progress_message)
        self.assertIn('current_prompt', progress_message)
        self.assertIn('status', progress_message)
        
        # Verify data types
        self.assertIsInstance(progress_message['current'], int)
        self.assertIsInstance(progress_message['total'], int)
        self.assertIsInstance(progress_message['current_prompt'], str)

if __name__ == '__main__':
    unittest.main()
