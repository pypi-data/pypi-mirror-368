from PIL import Image

def redimensionar(caminho_entrada, caminho_saida, largura, altura):
    """
    Redimensiona a imagem para a largura e altura especificadas.
    """
    imagem = Image.open(caminho_entrada)
    imagem = imagem.resize((largura, altura))
    imagem.save(caminho_saida)
