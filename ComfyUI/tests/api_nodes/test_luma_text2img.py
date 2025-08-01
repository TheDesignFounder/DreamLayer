import pytest
import os
import torch
from unittest.mock import patch, MagicMock, Mock
import requests

# Create a simple test that validates the node structure without importing ComfyUI modules
class TestLumaText2ImgNode:
    """Test suite for LumaText2ImgNode - Standalone version"""

    def test_node_file_exists(self):
        """Test that the LumaText2ImgNode file exists and can be read"""
        node_file_path = "comfy_api_nodes/nodes_luma.py"
        assert os.path.exists(node_file_path), f"Node file {node_file_path} does not exist"
        
        with open(node_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that the LumaText2ImgNode class is defined
        assert "class LumaText2ImgNode" in content
        assert "def api_call" in content
        assert "RETURN_TYPES = (IO.IMAGE,)" in content
        assert "API_NODE = True" in content
        assert "CATEGORY = \"api node/image/Luma\"" in content

    def test_node_docstring_content(self):
        """Test that the node docstring contains required information"""
        node_file_path = "comfy_api_nodes/nodes_luma.py"
        
        with open(node_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the LumaText2ImgNode class and extract its docstring
        class_start = content.find("class LumaText2ImgNode")
        if class_start == -1:
            pytest.fail("LumaText2ImgNode class not found")
        
        # Look for the docstring after the class definition
        docstring_start = content.find('"""', class_start)
        if docstring_start == -1:
            pytest.fail("LumaText2ImgNode docstring not found")
        
        docstring_end = content.find('"""', docstring_start + 3)
        if docstring_end == -1:
            pytest.fail("LumaText2ImgNode docstring not properly closed")
        
        docstring = content[docstring_start + 3:docstring_end]
        
        # Check for required sections
        assert "Generates images using Luma's text-to-image API" in docstring
        assert "chains after a CLIPTextEncode block" in docstring
        assert "LUMA_API_KEY environment variable" in docstring
        assert "Parameters:" in docstring
        assert "API Key Setup:" in docstring
        assert "export LUMA_API_KEY=" in docstring

    def test_node_mappings_exist(self):
        """Test that the node is properly registered in the mappings"""
        node_file_path = "comfy_api_nodes/nodes_luma.py"
        
        with open(node_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that the node is in NODE_CLASS_MAPPINGS
        assert '"LumaText2ImgNode": LumaText2ImgNode,' in content
        
        # Check that the node is in NODE_DISPLAY_NAME_MAPPINGS
        assert '"LumaText2ImgNode": "Luma Text to Image (Direct)",' in content

    def test_api_call_method_structure(self):
        """Test that the api_call method has the correct structure"""
        node_file_path = "comfy_api_nodes/nodes_luma.py"
        
        with open(node_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the api_call method
        method_start = content.find("def api_call")
        if method_start == -1:
            pytest.fail("api_call method not found")
        
        # Extract the method signature
        signature_start = content.find("(", method_start)
        signature_end = content.find("):", method_start)
        if signature_start == -1 or signature_end == -1:
            pytest.fail("api_call method signature not found")
        
        signature = content[method_start:signature_end + 2]
        
        # Check that required parameters are present
        assert "prompt: str" in signature
        assert "model: str" in signature
        assert "aspect_ratio: str" in signature
        assert "seed" in signature
        assert "unique_id: str = None" in signature

    def test_input_types_structure(self):
        """Test that the INPUT_TYPES method has the correct structure"""
        node_file_path = "comfy_api_nodes/nodes_luma.py"
        
        with open(node_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the LumaText2ImgNode class
        class_start = content.find("class LumaText2ImgNode")
        if class_start == -1:
            pytest.fail("LumaText2ImgNode class not found")
        
        # Look for the INPUT_TYPES method within the LumaText2ImgNode class
        input_types_start = content.find("def INPUT_TYPES", class_start)
        if input_types_start == -1:
            pytest.fail("INPUT_TYPES method not found in LumaText2ImgNode")
        
        # Find the end of the INPUT_TYPES method by looking for the next method or class
        next_method = content.find("def ", input_types_start + 1)
        next_class = content.find("class ", input_types_start + 1)
        
        # Find the earliest end point
        end_points = [next_method, next_class]
        end_points = [ep for ep in end_points if ep != -1]
        
        if end_points:
            method_end = min(end_points)
        else:
            method_end = len(content)
        
        method_content = content[input_types_start:method_end]
        
        # Check that required inputs are defined
        assert '"prompt"' in method_content
        assert '"model"' in method_content
        assert '"aspect_ratio"' in method_content
        assert '"seed"' in method_content
        assert '"unique_id"' in method_content

    def test_api_key_validation(self):
        """Test that the node validates API key presence"""
        node_file_path = "comfy_api_nodes/nodes_luma.py"
        
        with open(node_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that API key validation is implemented
        assert "os.environ.get('LUMA_API_KEY')" in content
        assert "LUMA_API_KEY environment variable is not set" in content
        assert "export LUMA_API_KEY=" in content

    def test_prompt_validation(self):
        """Test that the node validates prompt input"""
        node_file_path = "comfy_api_nodes/nodes_luma.py"
        
        with open(node_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that prompt validation is implemented
        assert "validate_string" in content
        assert "strip_whitespace=True" in content
        assert "min_length=3" in content

    def test_api_endpoint_structure(self):
        """Test that the API endpoint structure is correct"""
        node_file_path = "comfy_api_nodes/nodes_luma.py"
        
        with open(node_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that the correct API endpoint is used
        assert "/v1/images/generations" in content
        assert "HttpMethod.POST" in content
        assert "LumaImageGenerationRequest" in content
        assert "LumaGeneration" in content

    def test_polling_structure(self):
        """Test that the polling mechanism is implemented"""
        node_file_path = "comfy_api_nodes/nodes_luma.py"
        
        with open(node_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that polling is implemented
        assert "PollingOperation" in content
        assert "LumaState.completed" in content
        assert "LumaState.failed" in content
        assert "image_result_url_extractor" in content

    def test_image_processing(self):
        """Test that image processing is implemented"""
        node_file_path = "comfy_api_nodes/nodes_luma.py"
        
        with open(node_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that image processing is implemented
        assert "requests.get" in content
        assert "process_image_response" in content
        assert "return (img,)" in content

    def test_error_handling(self):
        """Test that proper error handling is implemented"""
        node_file_path = "comfy_api_nodes/nodes_luma.py"
        
        with open(node_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that error handling is implemented
        assert "raise ValueError" in content
        assert "Exception" in content

    def test_node_completeness(self):
        """Test that the node implementation is complete"""
        node_file_path = "comfy_api_nodes/nodes_luma.py"
        
        with open(node_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for all required components
        required_components = [
            "class LumaText2ImgNode",
            "RETURN_TYPES = (IO.IMAGE,)",
            "FUNCTION = \"api_call\"",
            "API_NODE = True",
            "CATEGORY = \"api node/image/Luma\"",
            "@classmethod",
            "def INPUT_TYPES",
            "def api_call",
            "validate_string",
            "os.environ.get('LUMA_API_KEY')",
            "SynchronousOperation",
            "PollingOperation",
            "requests.get",
            "process_image_response"
        ]
        
        for component in required_components:
            assert component in content, f"Required component '{component}' not found in node implementation"


if __name__ == "__main__":
    pytest.main([__file__]) 