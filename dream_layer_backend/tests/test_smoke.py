import dream_layer_backend.img2img_server


def test_import_backend():
    import dream_layer_backend
    assert dream_layer_backend is not None
    
    assert dream_layer_backend.img2img_server is not None