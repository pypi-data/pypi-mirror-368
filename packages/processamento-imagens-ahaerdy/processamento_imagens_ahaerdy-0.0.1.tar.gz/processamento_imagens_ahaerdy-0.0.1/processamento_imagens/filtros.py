from PIL import Image

def aplicar_filtro_pb(caminho_entrada, caminho_saida):
    """
    Converte a imagem para preto e branco.
    """
    imagem = Image.open(caminho_entrada).convert("L")
    imagem.save(caminho_saida)
