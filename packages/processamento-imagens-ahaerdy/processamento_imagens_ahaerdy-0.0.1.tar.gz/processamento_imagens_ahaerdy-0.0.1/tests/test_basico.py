def test_imports():
    from processamento_imagens import aplicar_filtro_pb, redimensionar
    assert callable(aplicar_filtro_pb)
    assert callable(redimensionar)
