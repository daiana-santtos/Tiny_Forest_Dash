import pygame as pg

from code.Const import WIN_WIDTH, GROUND_Y


class Player:
    def __init__(self, skin_id):
        self.skin_id = skin_id
        self.scale = 3.5

        #alocação de memória para os dicionários de sequências animadas
        self.frames = {'Run': [], 'Jump': [], 'Hurt': [], 'Death': []}
        self._load_frames()

        #alocação e carregamento condicional do efeito visual (VFX) de pulo duplo
        self.dust_frames = []
        self._load_dust()
        self.dust_active = False
        self.dust_pos = [0, 0]
        self.dust_idx = 0.0

        #estado inicial do ator e indexador de quadros de ponto flutuante
        self.state = 'Run'
        self.frame_idx = 0.0
        self.image = self.frames[self.state][0]
        self.rect = self.image.get_rect()

        #fixação de horizonte - ancora a base do jogador na Linha Mestra do cenário
        self.ground_y = GROUND_Y
        self.rect.midbottom = (int(WIN_WIDTH * 0.2), self.ground_y)

        #vetores de física cinemática no eixo Y
        self.vel_y = 0
        self.gravity = 0.75
        self.jump_power = -15.5

        #restrições de pulo duplo (acúmulo máximo de impulsos aéreos)
        self.max_jumps = 2
        self.current_jumps = 0

        #controle de temporizador de invulnerabilidade e efeito visual intermitente
        self.invencible = False
        self.invencible_timer = 0
        self.blink = False

    def _load_frames(self):
        """fatiador universal - recorta sub-superfícies baseando-se na proporção da cartela Run."""
        run_sheet = pg.image.load(f'asset/{self.skin_id}_Run.png').convert_alpha()
        frame_w = run_sheet.get_width() // 6
        frame_h = run_sheet.get_height()

        for anim_name in ['Run', 'Jump', 'Hurt', 'Death']:
            sheet = pg.image.load(f'asset/{self.skin_id}_{anim_name}.png').convert_alpha()
            count = sheet.get_width() // frame_w

            for i in range(count):
                frame = sheet.subsurface((i * frame_w, 0, frame_w, frame_h))
                scaled = pg.transform.scale(frame, (int(frame_w * self.scale), int (frame_h * self.scale)))
                self.frames[anim_name].append(scaled)

    def _load_dust(self):
        """carrega a folha de partículas estritamente se o recurso estiver presente no HD."""
        try:
            sheet = pg.image.load(f'asset/Double_Jump_Dust.png').convert_alpha()
            #fatiamento em grade quadrada - a largura de um quadro equivale à altura total do PNG
            size = sheet.get_height()
            count = sheet.get_width() // size
            for i in range(count):
                frame = sheet.subsurface((i * size, 0, size, size))
                self.dust_frames.append(pg.transform.scale(frame, (int(size * 2.5), int(size * 2.5))))
        except FileNotFoundError:
            pass    #tratamento de exceção silencioso para garantir resiliência de execução

    def jump(self):
        """aplica vetor de impulso no eixo Y respeitando o limite de pulos duplos."""
        if self.state == 'Death':
            return

        if self.current_jumps < self.max_jumps:
            self.vel_y = self.jump_power
            self.current_jumps += 1
            self.state = 'Jump'
            self.frame_idx = 0.0

            #gatilho de partícula - dispara a fumaça estritamente no segundo impulso aéreo
            if self.current_jumps == 2 and self.dust_frames:
                self.dust_active = True
                self.dust_idx = 0.0
                #posiciona o emissor na base central do polígono de colisão do jogador
                self.dust_pos = [self.rect.centerx - 30, self.rect.bottom - 20]

    def take_damage(self):
        """aplica estado de dano e ativa temporizador de imunidade, retorna True se houve dano real."""
        if not self.invencible and self.state != 'Death':
            self.state = 'Hurt'
            self.frame_idx = 0.0
            self.invencible = True
            self.invencible_timer = pg.time.get_ticks()
            return True
        return False

    def trigger_death(self):
        """interrompe o controle do jogador e aplica impulso cinemático de derrocada dramática."""
        if self.state != 'Death':
            self.state = 'Death'
            self.frame_idx = 0.0
            self.vel_y = -8.0 #impulso inicial para cima simulando impacto de arcade

    def update(self):
        """atualiza física cinemática e interpoladores de quadros da animação atual."""
        #integração de Euler - aplica aceleração da gravidade sobre a velocidade vetorial
        self.vel_y += self.gravity
        self.rect.y += int(self.vel_y)

        #ciclo de vida: estado morto
        if self.state == 'Death':
            if self.rect.bottom >= self.ground_y:
                self.rect.bottom = self.ground_y

            self.frame_idx += 0.12
            #trava no último quadro da animação e sinaliza conclusão para a transição de tela
            if self.frame_idx >= len(self.frames['Death']) - 1:
                self.frame_idx = len(self.frames['Death']) - 1
                return True #sinalizador booleano - animação de tragédia concluída

            self.image = self.frames['Death'][int(self.frame_idx)]
            return False

        #ciclo de vida: estado vivo
        #verificação de colisão estática com o solo
        if self.rect.bottom >= self.ground_y:
            self.rect.bottom = self.ground_y
            self.vel_y = 0
            self.current_jumps = 0 #restaura a capacidade de pulos ao tocar o chão

            if self.state == 'Jump':
                self.state = 'Run'
                self.frame_idx = 0.0  # <--- ADICIONE ESTA LINHA AQUI!

        #verificação de expiração do tempo de imunidade (duração de 1.5s)
        if self.invencible and (pg.time.get_ticks() - self.invencible_timer > 1500):
            self.invencible = False
            if self.state == 'Hurt':
                self.state = 'Run' if self.rect.bottom >= self.ground_y else 'Jump'

        #avanço do frame animado com controle de velocidade independente por estado
        anim_list = self.frames[self.state]
        if self.state == 'Hurt':
            speed = 0.12
        elif self.state == 'Jump':
            speed = 0.16
        else:
            speed = 0.25

        self.frame_idx += speed

        #estados e trava de animação
        if self.state == 'Jump':
            #impede o loop, travando no último frame útil da queda livre
            if self.frame_idx >= len(anim_list) - 1:
                self.frame_idx = len(anim_list) - 1

        elif self.state == 'Hurt':
            #retorna ao estado de repouso após o dano
            if self.frame_idx >= len(anim_list):
                self.state = 'Run' if self.rect.bottom >= self.ground_y else 'Jump'
                self.frame_idx = 0.0

        else:
            #loop com continuidade infinita para a corrida
            self.frame_idx %= len(anim_list)

        #atualiza o índice da imagem com base no índice calculado
        self.image = anim_list[int(self.frame_idx)]

        #recalcula o centro da base
        old_midbottom = self.rect.midbottom
        self.rect = self.image.get_rect()
        self.rect.midbottom = old_midbottom

        #atualização cinemática da partícula de fumaça (deslocamento contínuo pelo vento relativo)
        if self.dust_active:
            self.dust_pos[0] -= 3.5
            self.dust_idx += 0.25
            if self.dust_idx >= len(self.dust_frames):
                self.dust_active = False

        return False

    def draw(self, surface):
        #renderiza VFX em camada inferior (atrás do jogador)
        if self.dust_active:
            surface.blit(self.dust_frames[int(self.dust_idx)], self.dust_pos)

        #sprite flickering - omite a renderização em quadros alternados para simular invisibilidade
        if self.invencible:
            self.blink = not self.blink
            if self.blink:
                return
        surface.blit(self.image, self.rect)