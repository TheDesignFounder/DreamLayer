import pytest
import os
import torch
from unittest.mock import patch, MagicMock, Mock
import requests

# Helper functions to extract complex logic from tests
def get_node_file_content():
    """Helper function to get node file content"""
    node_file_path = "comfy_api_nodes/nodes_luma.py"
    with open(node_file_path, 'r', encoding='utf-8') as f:
        return f.read()

def find_class_in_content(content, class_name):
    """Helper function to find class in content"""
    return content.find(f"class {class_name}")

def find_method_in_content(content, method_name, start_pos=0):
    """Helper function to find method in content"""
    return content.find(f"def {method_name}", start_pos)

def extract_docstring(content, class_start):
    """Helper function to extract docstring"""
    docstring_start = content.find('"""', class_start)
    docstring_end = content.find('"""', docstring_start + 3)
    return content[docstring_start + 3:docstring_end]

def extract_method_signature(content, method_start):
    """Helper function to extract method signature"""
    signature_start = content.find("(", method_start)
    signature_end = content.find("):", method_start)
    return content[method_start:signature_end + 2]

def extract_input_types_method(content, class_start):
    """Helper function to extract INPUT_TYPES method content"""
    input_types_start = find_method_in_content(content, "INPUT_TYPES", class_start)
    next_method = content.find("def ", input_types_start + 1)
    next_class = content.find("class ", input_types_start + 1)
    
    end_points = [ep for ep in [next_method, next_class] if ep != -1]
    method_end = min(end_points) if end_points else len(content)
    
    return content[input_types_start:method_end]

def check_required_components(content, required_components):
    """Helper function to check required components"""
    missing_components = [comp for comp in required_components if comp not in content]
    return missing_components

# Create a simple test that validates the node structure without importing ComfyUI modules
class TestLumaText2ImgNode:
    """Test suite for LumaText2ImgNode - Standalone version"""

    def test_node_file_exists(self):
        """Test that the LumaText2ImgNode file exists and can be read"""
        node_file_path = "comfy_api_nodes/nodes_luma.py"
        assert os.path.exists(node_file_path), f"Node file {node_file_path} does not exist"
        
        content = get_node_file_content()
        
        # Check that the LumaText2ImgNode class is defined
        assert "class LumaText2ImgNode" in content
        assert "def api_call" in content
        assert "RETURN_TYPES = (IO.IMAGE,)" in content
        assert "API_NODE = True" in content
        assert "CATEGORY = \"api node/image/Luma\"" in content

    def test_node_docstring_content(self):
        """Test that the node docstring contains required information"""
        content = get_node_file_content()
        
        # Find the LumaText2ImgNode class and extract its docstring
        class_start = find_class_in_content(content, "LumaText2ImgNode")
        docstring = extract_docstring(content, class_start)
        
        # Check for required sections
        assert "Generates images using Luma's text-to-image API" in docstring
        assert "chains after a CLIPTextEncode block" in docstring
        assert "LUMA_API_KEY environment variable" in docstring
        assert "Parameters:" in docstring
        assert "API Key Setup:" in docstring
        assert "export LUMA_API_KEY=" in docstring

    def test_node_mappings_exist(self):
        """Test that the node is properly registered in the mappings"""
        content = get_node_file_content()
        
        # Check that the node is in NODE_CLASS_MAPPINGS
        assert '"LumaText2ImgNode": LumaText2ImgNode,' in content
        
        # Check that the node is in NODE_DISPLAY_NAME_MAPPINGS
        assert '"LumaText2ImgNode": "Luma Text to Image (Direct)",' in content

    def test_api_call_method_structure(self):
        """Test that the api_call method has the correct structure"""
        content = get_node_file_content()
        
        # Find the api_call method
        method_start = find_method_in_content(content, "api_call")
        signature = extract_method_signature(content, method_start)
        
        # Check that required parameters are present
        assert "prompt: str" in signature
        assert "model: str" in signature
        assert "aspect_ratio: str" in signature
        assert "seed" in signature
        assert "unique_id: str = None" in signature

    def test_input_types_structure(self):
        """Test that the INPUT_TYPES method has the correct structure"""
        content = get_node_file_content()
        
        # Find the LumaText2ImgNode class
        class_start = find_class_in_content(content, "LumaText2ImgNode")
        method_content = extract_input_types_method(content, class_start)
        
        # Check that required inputs are defined
        assert '"prompt"' in method_content
        assert '"model"' in method_content
        assert '"aspect_ratio"' in method_content
        assert '"seed"' in method_content
        assert '"unique_id"' in method_content

    def test_api_key_validation(self):
        """Test that the node validates API key presence"""
        content = get_node_file_content()
        
        # Check that API key validation is implemented
        assert "os.environ.get('LUMA_API_KEY')" in content
        assert "LUMA_API_KEY environment variable is not set" in content
        assert "export LUMA_API_KEY=" in content

    def test_prompt_validation(self):
        """Test that the node validates prompt input"""
        content = get_node_file_content()
        
        # Check that prompt validation is implemented
        assert "validate_string" in content
        assert "strip_whitespace=True" in content
        assert "min_length=3" in content

    def test_api_endpoint_structure(self):
        """Test that the API endpoint structure is correct"""
        content = get_node_file_content()
        
        # Check that the correct API endpoint is used
        assert "/v1/images/generations" in content
        assert "HttpMethod.POST" in content
        assert "LumaImageGenerationRequest" in content
        assert "LumaGeneration" in content

    def test_polling_structure(self):
        """Test that the polling mechanism is implemented"""
        content = get_node_file_content()
        
        # Check that polling is implemented
        assert "PollingOperation" in content
        assert "LumaState.completed" in content
        assert "LumaState.failed" in content
        assert "image_result_url_extractor" in content

    def test_image_processing(self):
        """Test that image processing is implemented"""
        content = get_node_file_content()
        
        # Check that image processing is implemented
        assert "requests.get" in content
        assert "process_image_response" in content
        assert "return (img,)" in content

    def test_error_handling(self):
        """Test that proper error handling is implemented"""
        content = get_node_file_content()
        
        # Check that error handling is implemented
        assert "raise ValueError" in content
        assert "Exception" in content

    @pytest.mark.parametrize("component", [
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
    ])
    def test_node_completeness(self, component):
        """Test that the node implementation is complete"""
        content = get_node_file_content()
        assert component in content, f"Required component '{component}' not found in node implementation"


if __name__ == "__main__":
    pytest.main([__file__]) 