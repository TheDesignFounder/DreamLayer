"""
Integration test for Runway Text2Img Node.
This test should be run when the full ComfyUI environment is available.
"""

import os
import sys
import ast
import pytest
import torch
import importlib.util
from unittest import mock

# --- Setup Helpers ---

def get_comfyui_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def get_nodes_file_path():
    return os.path.join(get_comfyui_root(), "comfy_api_nodes", "nodes_runway.py")

def read_nodes_file():
    with open(get_nodes_file_path(), "r") as f:
        return f.read()

# --- Fixtures ---

@pytest.fixture(scope="module", autouse=True)
def add_comfyui_to_sys_path():
    """Automatically add ComfyUI paths to sys.path for all tests."""
    comfyui_root = get_comfyui_root()
    current_dir = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, comfyui_root)
    sys.path.insert(0, current_dir)

# --- Tests ---

def test_nodes_file_exists():
    """Test that the node file exists."""
    assert os.path.exists(get_nodes_file_path()), "nodes_runway.py file is missing"

def test_runway_node_has_expected_content():
    """Test that expected strings exist in the source code."""
    content = read_nodes_file()
    
    expected_lines = [
        "class RunwayText2ImgNode",
        "RETURN_TYPES = (\"IMAGE\",)",
        "FUNCTION = \"generate_image\"",
        "CATEGORY = \"api node/image/Runway\"",
        "def generate_image(self, prompt: str, ratio: str, unique_id: Optional[str] = None",
        "RUNWAY_API_KEY",
    ]
    
    for line in expected_lines:
        assert line in content, f"Expected line missing: {line}"

def test_runway_node_ast_valid_and_has_generate_image():
    """Test that RunwayText2ImgNode and generate_image() exist via AST."""
    content = read_nodes_file()
    tree = ast.parse(content)

    class_defs = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    runway_node = next((cls for cls in class_defs if cls.name == "RunwayText2ImgNode"), None)

    assert runway_node is not None, "RunwayText2ImgNode class not found"

    func_defs = [f for f in runway_node.body if isinstance(f, ast.FunctionDef)]
    func_names = [f.name for f in func_defs]
    assert "generate_image" in func_names, "generate_image method not found in RunwayText2ImgNode"

    func = next(f for f in func_defs if f.name == "generate_image")
    arg_names = [arg.arg for arg in func.args.args]

    assert "prompt" in arg_names, "Missing 'prompt' argument"
    assert "ratio" in arg_names, "Missing 'ratio' argument"
    assert "unique_id" in arg_names, "Missing 'unique_id' argument"

def test_runway_node_mappings_exist():
    """Test NODE_CLASS_MAPPINGS and NODE_DISPLAY_NAME_MAPPINGS are present and valid."""
    content = read_nodes_file()
    assert "NODE_CLASS_MAPPINGS" in content, "NODE_CLASS_MAPPINGS not found"
    assert "RunwayText2ImgNode" in content, "RunwayText2ImgNode not in NODE_CLASS_MAPPINGS"
    assert "NODE_DISPLAY_NAME_MAPPINGS" in content, "NODE_DISPLAY_NAME_MAPPINGS not found"

def test_runway_node_import_with_mock_dependencies():
    """Test node file can be imported with mocked dependencies."""
    mock_modules = {
        'utils.json_util': mock.MagicMock(),
        'server': mock.MagicMock(),
        'comfy': mock.MagicMock(),
        'comfy.comfy_types': mock.MagicMock(),
        'comfy.comfy_types.node_typing': mock.MagicMock(),
    }

    with mock.patch.dict('sys.modules', mock_modules):
        spec = importlib.util.spec_from_file_location("nodes_runway", get_nodes_file_path())
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        assert hasattr(module, "RunwayText2ImgNode"), "RunwayText2ImgNode not found after import"
