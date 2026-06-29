import pygame as pg
from code.Const import WIN_WIDTH, WIN_HEIGHT, TITLE, C_WHITE, C_LAVENDER


class Menu:
    def __init__(self):
        #aloca as fontes padrão do sistema operacional com diferentes pesos visuais
        self.font_title = pg.font.Font(None, 72)
        self.font_subtitle = pg.font.Font(None, 48)
        self.font_controls = pg.font.Font(None, 26)
        #carrega o bg estático do menu e convert simples por não conter canal alpha
        self.bg_image = pg.image.load('asset/MenuBg.png').convert()
        self.bg_image = pg.transform.scale(self.bg_image, (WIN_WIDTH, WIN_HEIGHT))

        #vetor contendo as ramificações de estado disponíveis para o jogador
        self.options = ['New Game', 'Score', 'Exit']
        self.selected_index = 0 #índice começa com new game selecionado

    def handle_input(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP:
                #operador % (módulo) para o cursor dar a volta quando chega no topo
                self.selected_index = ((self.selected_index - 1) % len(self.options))

            elif event.key == pg.K_DOWN:
                #outro módulo para dar a volta quando chegar no último
                self.selected_index = ((self.selected_index + 1) % len(self.options))

            elif event.key in [pg.K_RETURN, pg.K_SPACE]:
                return self.options[self.selected_index]

        return None

    def draw(self, surface):
        surface.blit(self.bg_image, (0,0))
        #título centralizado no quarto superior da tela (25% do Y)
        title_surf = self.font_title.render(TITLE, True, C_WHITE)
        title_rect = title_surf.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT * 0.25))
        surface.blit(title_surf, title_rect)

        #desenha as opções dinamicamente
        for i, option_text in enumerate(self.options):
            if i == self.selected_index:
                #se o cursor estiver na opção, coloca as setinha e muda a cor
                text = f'> {option_text} <'
                color = C_LAVENDER
            else:
                text = option_text
                color = C_WHITE

            opt_surf = self.font_subtitle.render(text, True, color)

            #calcular altura y dando espaço de 60px entre cada linha
            y_position = (WIN_HEIGHT * 0.48) + (i * 60)
            opt_rect = opt_surf.get_rect(center=(WIN_WIDTH / 2, y_position))
            surface.blit(opt_surf, opt_rect)

        #exibir comandos na tela
        ctrl_text = 'CONTROLS: [UP]/[SPACE] Jump | [ESC] Go Back'
        ctrl_surf = self.font_controls.render(ctrl_text, True, C_WHITE)
        ctrl_rect = ctrl_surf.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT * 0.92))
        surface.blit(ctrl_surf, ctrl_rect)