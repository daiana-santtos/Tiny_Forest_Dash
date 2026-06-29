import pygame as pg
import sys
import random
from code.Const import WIN_WIDTH, WIN_HEIGHT, TITLE, FPS, C_BLACK, C_WHITE
from code.Background import Background
from code.Menu import Menu
from code.CharSelect import CharSelect
from code.Player import Player
from code.Obstacle import Obstacle
from code.Score import Score


class Game:
    def __init__(self):
        #inicializa os drivers de vídeo, som e periféricos do sistema operacional
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True

        #instancia as telas externas e subsistemas da máquina de estados
        self.bg = Background()
        self.menu = Menu()
        self.char_select = CharSelect()
        self.score_board = Score()  # <--- 2. INSTANCIANDO

        self.heart_img = pg.image.load(f'asset/heart.png').convert_alpha()

        #define o ponto de ignição da máquina de estados finitos
        self.state = 'MENU'
        self._play_music('music_menu')
        self.player_skin_id = 'Ch1'

    @staticmethod
    def _play_music(file_name, volume=0.3):
        """carrega a trilha em stream e toca em loop infinito (-1)."""
        try:
            pg.mixer.music.load(f"asset/{file_name}.wav")
            pg.mixer.music.set_volume(volume)
            pg.mixer.music.play(-1)
        except (FileNotFoundError, pg.error):
            pass  #silencia estritamente ausência do arquivo ou falta de hardware de áudio

    def _start_survival_arena(self):
        """inicializa os atores e variáveis da fase jogável"""
        self.player = Player(self.player_skin_id)
        self.obstacles = []
        self.lives = 3
        self.arena_start_ticks = pg.time.get_ticks()
        self.next_spawn_time = pg.time.get_ticks() + 1000 #primeiro obstaculo vem em 1s

        self.state = 'PLAYING'
        self._play_music('music_playing', 0.2)

    def run(self):
        while self.running:
            """loop principal do jogo, contendo as 3 fases de atualização"""
            self._check_events()    #captura de entradas (input)
            self._update()          #atualização de lógica e física
            self._draw()            #randerização gráfica (output)
            self.clock.tick(FPS)
        pg.quit()
        sys.exit()

    def _check_events(self):
        #varre a fila de eventos acionados pelo usuário no frame atual
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

            #modo: menu principal
            if self.state == 'MENU':
                action = self.menu.handle_input(event)
                if action == 'New Game':
                    self.state = 'CHAR_SELECT'
                elif action == 'Score':
                    self.score_board.set_view_mode() #ativa a visualização do top 10
                    self._play_music('music_score')
                    self.state = 'SCORE_BOARD'
                elif action == 'Exit':
                    self.running = False

            #modo: seleção de personagem
            elif self.state == 'CHAR_SELECT':
                chosen = self.char_select.handle_input(event)
                if chosen == 'BACK':
                    self.state = 'MENU'
                elif chosen in ['Ch0', 'Ch1', 'Ch2']:
                    self.player_skin_id = chosen
                    self._start_survival_arena() #dispara a transição para a gameplay

            #modo: placar de líderes
            elif self.state == 'SCORE_BOARD':
                action = self.score_board.handle_input(event)
                if action == 'MAIN_MENU':
                    self._play_music('music_menu')
                    self.state = 'MENU'

            #modo: jogando
            elif self.state == 'PLAYING':
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self._play_music('music_menu')
                        self.state = 'MENU'
                    #pular com up ou espaço
                    elif event.key in [pg.K_SPACE, pg.K_UP]:
                        self.player.jump()

    def _update(self):
        if self.state == 'PLAYING':
            self.bg.update()
            #atualiza o herói e verefica se a animação de morte foi concluída
            death_is_finished = self.player.update()
            #matemática do relógio - 60s progressivos
            survived_seconds = (pg.time.get_ticks() - self.arena_start_ticks) // 1000
            self.time_left = max(0, 60 - survived_seconds)

            #condição de vitória - contador chegou a zero
            if self.time_left == 0:
                self.score_board.set_input_mode(60)
                self._play_music('music_score')
                self.state = 'SCORE_BOARD'
                return

            #gerador de obstaculos
            #verifica se o relógio interno ultrapassou a meta agendada e se o herói está vivo
            if pg.time.get_ticks() > self.next_spawn_time and self.player.state != 'Death':
                self.obstacles.append(Obstacle())
                # sorteia o intervalo da próxima pedra entre 1.1 e 2.3 segundos na fila
                self.next_spawn_time = pg.time.get_ticks() + random.randint(1100, 2300)

            #gerenciador de colisão e limpeza de entidades
            for obs in self.obstacles[:]:
                obs.update()

                #só processa física de colisão se o jogador ainda estiver no estado jogável
                if self.player.state != 'Death':
                    # o .inflate(-18, -10) reduz a hitbox invisível para perdoar raspões visuais
                    if self.player.rect.inflate(-18, -10).colliderect(obs.rect):
                        if self.player.take_damage():
                            self.lives -= 1
                            #dispara a morte se o contador de vidas zerar
                            if self.lives <= 0:
                                self.player.trigger_death()

                #garbage collection - remove objetos que saíram da tela pela esquerda
                if obs.is_off_screen():
                    self.obstacles.remove(obs)

            #transição de estado - aguarda o último quadro da animação de morte terminar
            if death_is_finished:
                self.score_board.set_input_mode(survived_seconds)
                self._play_music('music_score')
                self.state = 'SCORE_BOARD'

    def _draw(self):
        #limpa o buffer de vídeo anterior
        self.screen.fill(C_BLACK)

        #roteador de desenho por estado
        if self.state == 'MENU':
            self.menu.draw(self.screen)

        elif self.state == 'CHAR_SELECT':
            self.char_select.draw(self.screen)

        elif self.state == 'SCORE_BOARD':
            self.score_board.draw(self.screen)


        elif self.state == 'PLAYING':
            #respeita a ordem das imagens
            self.bg.draw(self.screen)

            for obs in self.obstacles:
                obs.draw(self.screen)

            self.player.draw(self.screen)

            #desenha os ícone de vida com espaçamento de 50px entre eles no eixo X
            for i in range(self.lives):
                self.screen.blit(self.heart_img, (20 + (i * 50), 20))

            #instanciação dinâmica da tipografia nativa para o temporizador
            font = pg.font.Font(None, 48)
            t_surf = font.render(f'{self.time_left}s', True, C_WHITE)
            self.screen.blit(t_surf, t_surf.get_rect(topright=(WIN_WIDTH - 30, 25)))

        #troca os buffers de vídeo, exibindo o quadro final
        pg.display.flip()