import unittest
from unittest.mock import patch
import torch
import numpy as np
import os
import hashlib
from io import BytesIO
from comfy_api_nodes.recraft_vectorize import RecraftVectorizeNode

class TestRecraftVectorizeNode(unittest.TestCase):
    """
    Unit test for the RecraftVectorizeNode.
    """
    def setUp(self):
        """Set up the environment for each test case."""
        self.node = RecraftVectorizeNode()
        self.output_dir = "output/test_svgs"
        # Create a consistent dummy image for deterministic hashing
        dummy_array = np.zeros((64, 64, 3), dtype=np.uint8)
        dummy_array[16:48, 16:48, :] = 128
        self.image_tensor = torch.from_numpy(dummy_array.astype(np.float32) / 255.0).unsqueeze(0)
        # Define the exact SVG content our mock API will return
        self.mock_svg_content = '<svg width="64" height="64"><rect x="16" y="16" width="32" height="32" fill="#808080"/></svg>'
        # Define mock authentication arguments for the API call
        self.mock_auth_kwargs = {'auth_token': 'test_token'}


    def tearDown(self):
        """Clean up any files or directories created during tests."""
        if os.path.exists(self.output_dir):
            for f in os.listdir(self.output_dir):
                os.remove(os.path.join(self.output_dir, f))
            os.rmdir(self.output_dir)

    @patch('comfy_api_nodes.recraft_vectorize.handle_recraft_file_request')
    def test_execute_verifies_api_call_and_saves_file(self, mock_api_call):
        """
        GIVEN a raster image tensor
        WHEN the node's execute method is called
        THEN it should call the API with the correct parameters and save the file correctly.
        """
        # setup MOCK
        mock_api_call.return_value = [BytesIO(self.mock_svg_content.encode('utf-8'))]
        result_path_str, = self.node.execute(
            image=self.image_tensor,
            resolution_limit=1024,
            output_path=self.output_dir,
            **self.mock_auth_kwargs
        )
        result_path = result_path_str.strip()

        # Verify the API was called with the correct parameters
        mock_api_call.assert_called_once()
        call_kwargs = mock_api_call.call_args.kwargs
        self.assertTrue(torch.equal(call_kwargs['image'], self.image_tensor))
        self.assertEqual(call_kwargs['path'], "/proxy/recraft/images/vectorize")
        self.assertEqual(call_kwargs['auth_kwargs'], self.mock_auth_kwargs)

        # Verify the SVG file was created correctly
        self.assertTrue(os.path.exists(result_path))
        self.assertEqual(os.path.getsize(result_path), len(self.mock_svg_content.encode('utf-8')))

        # Verify the checksum of the ENTIRE file for accurate validation
        with open(result_path, 'rb') as f:
            checksum = hashlib.sha256(f.read()).hexdigest()
        expected_checksum = hashlib.sha256(self.mock_svg_content.encode('utf-8')).hexdigest()
        self.assertEqual(checksum, expected_checksum)
