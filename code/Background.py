import pygame as pg

from code.Const import BG_SPEED, WIN_WIDTH, WIN_HEIGHT


class Background:
    def __init__(self):
        #lista vazia pra guardar as camadas
        self.layers = []
        #.items() desempacota o dicionário em tuplas dinâmicas (nome_arquivo, velocidade_relativa)
        for bg_name, speed in BG_SPEED.items():
            image = pg.image.load('asset/' + bg_name + '.png').convert_alpha()
            image = pg.transform.scale(image, (WIN_WIDTH, WIN_HEIGHT))

            #cada camada mantém duas instâncias gêmeas para cobrir a área de transição
            self.layers.append(
                {
                    'image': image,
                    'copy1': 0,
                    'copy2': WIN_WIDTH,     #nasce exatamente colada na borda direita da cópia 1
                    'speed': speed
                }
            )

    def update(self): #acionado 60x por seg
        """atualizado a 60fps pelo game loop para deslocar as coordenadas X"""
        for layer in self.layers:
            #aplica velocidade vetorial negativa, empurrando o cenário para a esquerda
            layer['copy1'] -= layer['speed']
            layer['copy2'] -= layer['speed']

            #correção de overshoot - em vez de cravar coordenada fixa (+960), amarramos
            #matematicamente a ponta da cópia que saiu na cauda da cópia que ficou na tela.
            if layer['copy1'] <= -WIN_WIDTH:
                layer['copy1'] = layer['copy2'] + WIN_WIDTH

            if layer['copy2'] <= -WIN_WIDTH:
                layer['copy2'] = layer['copy1'] + WIN_WIDTH

    def draw(self, surface):
        for layer in self.layers:
            #blit (block transfer) - carimba a matriz de pixels das duas cópias na tela principal
            surface.blit(layer['image'], (layer['copy1'], 0))
            surface.blit(layer['image'], (layer['copy2'], 0))