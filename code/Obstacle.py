import pygame as pg
import random

from code.Const import  WIN_WIDTH, GROUND_Y


class Obstacle:
    def __init__(self):
        #distribuição estocástica - 65% de chance de obstáculo baixo (pulo simples)
        #e 35% de chance de obstáculo colossal (exige pulo duplo)
        self.type = random.choices(['SMALL', 'LARGE'], weights=[0.65, 0.35])[0]

        try:
            self.image = pg.image.load('asset/Rock.png').convert_alpha()

            #escalonamento dinâmico procedural para que nenhuma rocha seja 100% igual à outra
            if self.type == 'SMALL':
                scale = random.uniform(2.2, 2.6)
            else:
                scale = random.uniform(3.8, 4.3)

            w, h = int(self.image.get_width() * scale), int(self.image.get_height() * scale)
            self.image = pg.transform.smoothscale(self.image, (w, h))

        except FileNotFoundError:
            #resiliência de software - se o PNG não existir no PC, gera um polígono de teste
            #em vez de permitir que o jogo encerre com Crash (Exceção tratada).
            h = 35 if self.type == 'SMALL' else 75
            self.image = pg.Surface((45, h), pg.SRCALPHA)
            pg.draw.rect(self.image, (120, 110, 110), (0, 0, 45, h))

        self.rect = self.image.get_rect()

        #se a pedra é gigante, afundamos a base dela 4px a mais na grama pra assentar
        offset_y = GROUND_Y if self.type == "SMALL" else GROUND_Y + 4

        #spawn com atraso aleatório no eixo X (fora da tela pela direita)
        self.rect.midbottom = (WIN_WIDTH + random.randint(30, 150), offset_y)
        self.speed = random.uniform(7.0, 11.0)

    def update(self):
        """desloca a caixa de colisão (hitbox) em direção ao jogador"""
        self.rect.x -= int(self.speed)

    def is_off_screen(self):
        """sinalizador booleano para o garbage collector limpar a memória"""
        return self.rect.right < 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)