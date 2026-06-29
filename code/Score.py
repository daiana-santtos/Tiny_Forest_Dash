import pygame as pg
from code.Database import Database
from code.Const import WIN_WIDTH, WIN_HEIGHT, C_WHITE, C_LAVENDER, C_GRAY2, C_GRAY1


class Score:
    def __init__(self):
        #instancia a camada de persistência para gravação e leitura
        self.db = Database()
        self.bg_image = pg.image.load('asset/ScoreBg.png').convert()
        self.bg_image = pg.transform.scale(self.bg_image, (WIN_WIDTH, WIN_HEIGHT))

        #hierarquia visual tipográfica
        self.font_title = pg.font.Font(None, 64)
        self.font_sub = pg.font.Font(None, 42)
        self.font_list = pg.font.Font(None, 36)
        self.font_ctrl = pg.font.Font(None, 26)

        #estado interno de exibição - input para registro e view para consulta
        self.mode = 'VIEW'

        #vetor de caracteres - aloca 4 bytes com o valor decimal 65 (letra 'A')
        self.initials = [65, 65, 65, 65]
        self.letter_idx = 0
        self.time_achieved = 0

    def set_input_mode(self, time_achieved):
        """prepara o buffer de digitação para registrar novo recorde"""
        self.mode = 'INPUT'
        self.initials = [65, 65, 65, 65]
        self.letter_idx = 0
        self.time_achieved = time_achieved

    def set_view_mode(self):
        """alterna a tela para o modo estático de leitura do top 10"""
        self.mode = 'VIEW'

    def handle_input(self, event):
        """roteador de eventos de hardware para navagação e digitação"""
        if event.type == pg.KEYDOWN:
            #entrada de dados - registros iniciais
            if self.mode == "INPUT":
                if event.key == pg.K_LEFT:
                    self.letter_idx = (self.letter_idx - 1) % 4

                elif event.key == pg.K_RIGHT:
                    self.letter_idx = (self.letter_idx + 1) % 4

                elif event.key == pg.K_UP:
                    #incrementa o caractere ciclicamente dentro do alfabeto (A..Z)
                    curr = self.initials[self.letter_idx]
                    self.initials[self.letter_idx] = 65 + ((curr - 65 + 1) % 26)

                elif event.key == pg.K_DOWN:
                    # incrementa o caractere ciclicamente dentro do alfabeto (A..Z)
                    curr = self.initials[self.letter_idx]
                    self.initials[self.letter_idx] = 65 + ((curr - 65 - 1) % 26)

                #captura direta de teclado nativo - filtra caracteres acentuados ou símbolos
                elif event.unicode.isalpha() and event.unicode.isascii():
                    char_typed = event.unicode.upper()
                    self.initials[self.letter_idx] = ord(char_typed)    #converte letra para decimal ASCII
                    self.letter_idx = (self.letter_idx + 1) % 4         #avança cursor automaticamente

                elif event.key == pg.K_BACKSPACE:
                    self.letter_idx = (self.letter_idx - 1) % 4
                    self.initials[self.letter_idx] = 65 #restaura o valor padrão 'A'

                elif event.key == pg.K_RETURN:
                    #decodifica os inteiros ASCII em string (ex: [68, 65, 78, 73] -> "DANI")
                    player_name = "".join([chr(c) for c in self.initials])
                    self.db.save_score(player_name, self.time_achieved)
                    self.mode = "VIEW" #redireciona imediatamente para a tela de recordes

            #consulta - hall da fama
            elif self.mode == "VIEW":
                if event.key == pg.K_ESCAPE:
                    return "MAIN_MENU"

        return None

    def draw(self, surface):
        surface.blit(self.bg_image, (0, 0))

        #randerização - modo de cadastro
        if self.mode == "INPUT":
            t_surf = self.font_title.render("GAME OVER - ENTER YOUR NAME", True, C_LAVENDER)
            surface.blit(t_surf, t_surf.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT * 0.2)))

            time_msg = f"Time Survived: {self.time_achieved} Seconds"
            sub_surf = self.font_list.render(time_msg, True, C_WHITE)
            surface.blit(sub_surf, sub_surf.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT * 0.32)))

            #cálculo de centralização em bloco - span total de 240px distribuídos em X
            start_x = (WIN_WIDTH / 2) - 120

            for i in range(4):
                char_str = chr(self.initials[i])
                x_pos = start_x + (i * 80)

                #aplica realce de foco (cor exclusiva e indicadores de navegação ^ v)
                if i == self.letter_idx:
                    c_surf = self.font_title.render(char_str, True, C_LAVENDER)
                    up_arr = self.font_ctrl.render("^", True, C_LAVENDER)
                    dw_arr = self.font_ctrl.render("v", True, C_LAVENDER)
                    surface.blit(up_arr, up_arr.get_rect(center=(x_pos, WIN_HEIGHT * 0.45)))
                    surface.blit(dw_arr, dw_arr.get_rect(center=(x_pos, WIN_HEIGHT * 0.65)))
                else:
                    c_surf = self.font_title.render(char_str, True, C_WHITE)

                surface.blit(c_surf, c_surf.get_rect(center=(x_pos, WIN_HEIGHT * 0.55)))

            ctrl_surf = self.font_ctrl.render("CONTROLS: [UP]/[DOWN] Letter   |   [LEFT]/[RIGHT] Move   |   [ENTER] Confirm", True, C_GRAY2)
            surface.blit(ctrl_surf, ctrl_surf.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT * 0.9)))

        #randerização - modo hall da fama
        elif self.mode == 'VIEW':
            t_surf = self.font_title.render('HALL OF FAME', True, C_LAVENDER)
            surface.blit(t_surf, t_surf.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT * 0.12)))
            top_scores = self.db.get_top_10()

            header_surf = self.font_ctrl.render("RANK                 NAME                 SURVIVAL TIME", True, C_GRAY1)
            surface.blit(header_surf, header_surf.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT * 0.25)))

            y_start = WIN_HEIGHT * 0.32
            for i, (name, time_s) in enumerate(top_scores):
                #pódio em destaque aplica a cor pastel C_LAVENDER aos Top 3 colocados
                color = C_LAVENDER if i < 3 else C_WHITE
                row_str = f"#{i+1:02d}                       {name}                       {time_s}s"
                row_surf = self.font_list.render(row_str, True, color)
                surface.blit(row_surf, row_surf.get_rect(center=(WIN_WIDTH / 2, y_start + (i * 40))))

            esc_surf = self.font_ctrl.render("Press [ESC] to return to Main Menu", True, C_GRAY2)
            surface.blit(esc_surf, esc_surf.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT * 0.92)))