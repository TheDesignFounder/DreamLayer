"""
Unit tests for constants validation
"""
import unittest
import re
from constants import (
    DIMENSION_LIMITS, BATCH_SIZE_LIMITS, SAMPLING_LIMITS,
    SEED_LIMITS, BASE64_DETECTION, DEFAULT_PATHS,
    CONTROLNET_TYPE_MAPPING, SERVER_CONFIG
)


class TestConstants(unittest.TestCase):
    """Test that constants are properly defined and valid"""

    def test_dimension_limits(self):
        """Test dimension limit constants"""
        self.assertGreater(DIMENSION_LIMITS['MIN'], 0)
        self.assertGreater(DIMENSION_LIMITS['MAX'], DIMENSION_LIMITS['MIN'])
        self.assertGreaterEqual(DIMENSION_LIMITS['DEFAULT'], DIMENSION_LIMITS['MIN'])
        self.assertLessEqual(DIMENSION_LIMITS['DEFAULT'], DIMENSION_LIMITS['MAX'])
        
        # Test specific values
        self.assertEqual(DIMENSION_LIMITS['MIN'], 64)
        self.assertEqual(DIMENSION_LIMITS['MAX'], 2048)
        self.assertEqual(DIMENSION_LIMITS['DEFAULT'], 512)

    def test_batch_size_limits(self):
        """Test batch size limit constants"""
        self.assertGreater(BATCH_SIZE_LIMITS['MIN'], 0)
        self.assertGreater(BATCH_SIZE_LIMITS['MAX'], BATCH_SIZE_LIMITS['MIN'])
        self.assertGreaterEqual(BATCH_SIZE_LIMITS['DEFAULT'], BATCH_SIZE_LIMITS['MIN'])
        self.assertLessEqual(BATCH_SIZE_LIMITS['DEFAULT'], BATCH_SIZE_LIMITS['MAX'])

    def test_sampling_limits(self):
        """Test sampling parameter limits"""
        # Steps
        steps = SAMPLING_LIMITS['STEPS']
        self.assertGreater(steps['MIN'], 0)
        self.assertGreater(steps['MAX'], steps['MIN'])
        self.assertGreaterEqual(steps['DEFAULT'], steps['MIN'])
        self.assertLessEqual(steps['DEFAULT'], steps['MAX'])

        # CFG Scale
        cfg = SAMPLING_LIMITS['CFG_SCALE']
        self.assertGreater(cfg['MIN'], 0)
        self.assertGreater(cfg['MAX'], cfg['MIN'])
        self.assertGreaterEqual(cfg['DEFAULT'], cfg['MIN'])
        self.assertLessEqual(cfg['DEFAULT'], cfg['MAX'])

    def test_seed_limits(self):
        """Test seed generation limits"""
        self.assertEqual(SEED_LIMITS['MIN_VALUE'], 0)
        self.assertEqual(SEED_LIMITS['MAX_VALUE'], 2**32 - 1)
        self.assertGreater(SEED_LIMITS['MAX_VALUE'], SEED_LIMITS['MIN_VALUE'])

    def test_base64_detection(self):
        """Test base64 detection constants"""
        self.assertGreater(BASE64_DETECTION['MIN_LENGTH'], 0)
        self.assertIsInstance(BASE64_DETECTION['PREFIXES'], list)
        self.assertIn('data:image', BASE64_DETECTION['PREFIXES'])
        self.assertIn('/9j/', BASE64_DETECTION['PREFIXES'])
        
        # Test regex pattern is valid
        pattern = BASE64_DETECTION['PATTERN']
        self.assertIsInstance(pattern, str)
        # Should compile without error
        compiled_pattern = re.compile(pattern)
        self.assertIsNotNone(compiled_pattern)

    def test_default_paths(self):
        """Test default path constants"""
        self.assertIsInstance(DEFAULT_PATHS['CONTROLNET_INPUT'], str)
        self.assertIsInstance(DEFAULT_PATHS['COMFYUI_INPUT_DIR'], str)
        self.assertTrue(DEFAULT_PATHS['CONTROLNET_INPUT'].endswith('.png'))

    def test_controlnet_type_mapping(self):
        """Test ControlNet type mapping"""
        expected_types = ['openpose', 'canny', 'depth', 'normal', 'segment', 'tile', 'repaint']
        
        for control_type in expected_types:
            self.assertIn(control_type, CONTROLNET_TYPE_MAPPING)
            self.assertIsInstance(CONTROLNET_TYPE_MAPPING[control_type], str)
        
        # Test specific mappings
        self.assertEqual(CONTROLNET_TYPE_MAPPING['openpose'], 'openpose')
        self.assertEqual(CONTROLNET_TYPE_MAPPING['canny'], 'canny/lineart/anime_lineart/mlsd')

    def test_server_config(self):
        """Test server configuration constants"""
        ports = SERVER_CONFIG['PORTS']
        hosts = SERVER_CONFIG['HOSTS']
        
        # Test ports are valid
        for _port_name, port_value in ports.items():
            self.assertIsInstance(port_value, int)
            self.assertGreater(port_value, 1000)  # Should be > 1024 for user ports
            self.assertLess(port_value, 65536)    # Valid port range
        
        # Test hosts are valid URLs
        for _host_name, host_value in hosts.items():
            self.assertIsInstance(host_value, str)
            self.assertTrue(host_value.startswith('http'))


class TestConstantUsage(unittest.TestCase):
    """Test how constants are used in validation functions"""

    def test_dimension_validation(self):
        """Test dimension validation using constants"""
        # Simulate the validation logic from txt2img_workflow.py
        def validate_dimension(value):
            return max(DIMENSION_LIMITS['MIN'], min(DIMENSION_LIMITS['MAX'], int(value)))
        
        # Test edge cases
        self.assertEqual(validate_dimension(32), DIMENSION_LIMITS['MIN'])  # Below min
        self.assertEqual(validate_dimension(3000), DIMENSION_LIMITS['MAX'])  # Above max
        self.assertEqual(validate_dimension(512), 512)  # Normal value

    def test_batch_size_validation(self):
        """Test batch size validation using constants"""
        def validate_batch_size(value):
            return max(BATCH_SIZE_LIMITS['MIN'], min(BATCH_SIZE_LIMITS['MAX'], int(value)))
        
        self.assertEqual(validate_batch_size(0), BATCH_SIZE_LIMITS['MIN'])
        self.assertEqual(validate_batch_size(10), BATCH_SIZE_LIMITS['MAX'])
        self.assertEqual(validate_batch_size(4), 4)

    def test_seed_generation(self):
        """Test seed generation using constants"""
        import random
        
        # Simulate seed generation logic
        for _ in range(10):
            seed = random.randint(SEED_LIMITS['MIN_VALUE'], SEED_LIMITS['MAX_VALUE'])
            self.assertGreaterEqual(seed, SEED_LIMITS['MIN_VALUE'])
            self.assertLessEqual(seed, SEED_LIMITS['MAX_VALUE'])

    def test_base64_detection_logic(self):
        """Test base64 detection using constants"""
        def is_base64_data(input_string):
            return (any(input_string.startswith(prefix) for prefix in BASE64_DETECTION['PREFIXES']) or
                   (re.match(BASE64_DETECTION['PATTERN'], input_string) and 
                    len(input_string) > BASE64_DETECTION['MIN_LENGTH']))
        
        # Test cases
        self.assertTrue(is_base64_data('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...'))
        self.assertTrue(is_base64_data('/9j/4AAQSkZJRgABAQAAAQABAAD/2wBD...'))
        self.assertFalse(is_base64_data('image.png'))
        self.assertFalse(is_base64_data('short'))


if __name__ == '__main__':
    unittest.main()