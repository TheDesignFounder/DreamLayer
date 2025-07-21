# Import the node class we want to test
from comfy_api_nodes.runway.runway_img2img import RunwayImg2Img

def test_runway_node_instantiation():
    # Test if the node can be instantiated without error
    node = RunwayImg2Img()
    assert node is not None  # The node should be successfully created

def test_runway_node_process():
    # Test if the process method works as expected with mock input
    node = RunwayImg2Img()
    input_image = "input_image.png"  # Simulated input image path or name
    reference_image = "reference_image.png"  # Simulated reference image
    result = node.process(input_image, reference_image)
    
    # Check that the result is a string and contains the expected output
    assert isinstance(result, str)
    assert "Processed" in result
