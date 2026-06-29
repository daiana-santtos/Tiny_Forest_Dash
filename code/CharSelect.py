import pygame as pg

from code.Const import WIN_WIDTH, WIN_HEIGHT, C_WHITE, C_LAVENDER, C_GRAY3, C_GRAY1


class CharSelect:
    def __init__(self):
        #tipografia hierarquizada para a interface de seleção
        self.font_title = pg.font.Font(None, 64)
        self.font_sub = pg.font.Font(None, 36)
        self.font_ctrl = pg.font.Font(None, 26)

        #reaproveita a abóbada estática de fundo - .convert() para otimização de VRAM
        self.bg_image = pg.image.load('asset/ScoreBg.png').convert()
        self.bg_image = pg.transform.scale(self.bg_image, (WIN_WIDTH, WIN_HEIGHT))

        #alocação dinâmica de sprites estáticos recortados
        self.avatars = []
        for i in range(3):
            img = pg.image.load(f'asset/Avatar{i}.png').convert_alpha()

            #amplia a malha geométrica 4x mantendo bordas rígidas
            w = img.get_width() * 4
            h = img.get_height() * 4
            img_scaled = pg.transform.scale(img, (w, h))
            self.avatars.append(img_scaled)

        self.selected_index = 1 #inicia com foco central no "hoodie"
        self.hero_names = ['Pinky', 'Hoodie', 'Bluey']

    def handle_input(self, event):
        """processa a navegação horizontal e devolve o ID de skin focado"""
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_LEFT:
                #aritmética Modular (%) - rotaciona o foco ciclicamente à esquerda (0 -> 2)
                self.selected_index = (self.selected_index - 1) % 3

            elif event.key == pg.K_RIGHT:
                #aritmética Modular (%) - rotaciona o foco ciclicamente à direita (2 -> 0)
                self.selected_index = (self.selected_index + 1) % 3

            elif event.key in [pg.K_RETURN, pg.K_SPACE]:
                #devolve a exata string que o Game.py está esperando ('Ch0', Ch1'...)
                return f'Ch{self.selected_index}'

            elif event.key == pg.K_ESCAPE:
                return 'BACK'
        return None

    def draw(self, surface):
        surface.blit(self.bg_image, (0, 0))

        title_surf = self.font_title.render('CHOOSE YOUR HERO', True, C_WHITE)
        surface.blit(title_surf, title_surf.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT * 0.18)))

        #coordenadas dos 3 bonecos - marcos em 28%, 50% e 72% do eixo X
        positions_x = [WIN_WIDTH * 0.28, WIN_WIDTH * 0.50, WIN_WIDTH * 0.72]
        y_pos = WIN_HEIGHT * 0.48

        for i in range(3):
            avatar_surf = self.avatars[i]
            avatar_rect = avatar_surf.get_rect(center=(positions_x[i], y_pos))

            if i == self.selected_index:
                #efeito de foco - moldura expandida (24px) com bordas arredondadas e cor C_LAVENDER
                box = avatar_rect.inflate(24, 24)
                pg.draw.rect(surface, C_LAVENDER, box, width=4, border_radius=12)
                name_surf = self.font_sub.render(f'< {self.hero_names[i]} >', True, C_LAVENDER)
            else:
                name_surf = self.font_sub.render(self.hero_names[i], True, C_GRAY1)

            surface.blit(avatar_surf, avatar_rect)
            #offset vertical (+100px) para assentar o rótulo de texto abaixo da caixa
            surface.blit(name_surf, name_surf.get_rect(center=(positions_x[i], y_pos + 100)))

        ctrl_surf = self.font_ctrl.render('CONTROLS: [LEFT]/[RIGHT] Select | [ENTER] Confirm | [ESC] Main Menu', True, C_GRAY3)
        surface.blit(ctrl_surf, ctrl_surf.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT * 0.92)))