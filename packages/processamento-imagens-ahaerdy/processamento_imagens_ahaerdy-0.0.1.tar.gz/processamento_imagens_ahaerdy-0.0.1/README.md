# processamento-imagens

Pacote simples para aplicar transformações e filtros em imagens usando Python e Pillow.

## Instalação
```bash
pip install processamento-imagens
```

## Uso
```python
from processamento_imagens import aplicar_filtro_pb, redimensionar

# Converter para preto e branco
aplicar_filtro_pb("entrada.jpg", "saida_pb.jpg")

# Redimensionar
redimensionar("entrada.jpg", "saida_red.jpg", 200, 200)
```

## Requisitos
- Python >= 3.8
- Pillow
