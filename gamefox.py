import pgzrun
import math
import random
from pygame import Rect
# from pgzero.builtins import mouse

# Configurações da tela
WIDTH = 800
HEIGHT = 600
TITLE = "Platformer Fox - Game"

# Estados do jogo
MENU = 0
PLAYING = 1
GAME_OVER = 2
game_state = MENU

# Variáveis do jogo
score = 0         # Pontuação do jogador
lives = 3         # Vidas do jogador
acorns = []       # Lista das moedas animadas

# Configurações do jogo
GRAVITY = 0.5
JUMP_STRENGTH = -12
PLAYER_SPEED = 3
ENEMY_SPEED = 1
BULLET_SPEED = 8
platforms = [
    Rect(450, HEIGHT - 200, 200, 20),
    Rect(200, HEIGHT - 320, 180, 20)]  # lista de plataformas

# Configurações de som
music_enabled = True

# Timer Instrucoes
instruction_timer = 400

class AnimatedSprite:
    """Classe base para sprites animados"""
    def __init__(self, x, y, frames, animation_speed=0.2):
        self.x = x
        self.y = y
        self.frames = frames  # Lista de nomes dos frames
        self.current_frame = 0
        self.animation_speed = animation_speed
        self.animation_timer = 0
        self.width = 32  # Tamanho padrão do sprite
        self.height = 32
        
    def update_animation(self):
        """Atualiza a animação do sprite"""
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.current_frame = (self.current_frame
                                  + 1) % len(self.frames)
    
    def get_current_frame(self):
        """Retorna o frame atual da animação"""
        frame = self.frames[self.current_frame]
        if hasattr(self, "facing_right") and not self.facing_right:
            return frame + "-flip" # Adiciona o nome a imagem espelhar
        return frame
    
    def get_rect(self):
        """Retorna o retângulo de colisão"""
        return Rect(self.x, self.y, self.width, self.height)

class Player(AnimatedSprite):
    """Classe do jogador com movimentação e animação"""
    def __init__(self, x, y):
        # Frames de animação do player
        idle_frames = [f'player-idle-{i}' 
                       for i in range(1, 5)]  # 4 frames idle
        walk_frames = [f'player-run-{i}' 
                       for i in range(1, 7)]  # 6 frames walk
        jump_frames = [f'player-jump-{i}' 
                       for i in range(1, 3)]  # 2 frames jump
        
        super().__init__(x, y, idle_frames, 0.15)
        
        self.idle_frames = idle_frames
        self.walk_frames = walk_frames
        self.jump_frames = jump_frames
        
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.state = "idle"  # idle, walking, jumping
        
        # Configurações de tiro
        self.shoot_cooldown = 0
        
    def update(self):
        """Atualiza o jogador"""
        # Controles de movimento
        keys = keyboard
        self.vel_x = 0
        
        if keys.left or keys.a:
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
            if self.on_ground:
                self.state = "walking"
        elif keys.right or keys.d:
            self.vel_x = PLAYER_SPEED
            self.facing_right = True
            if self.on_ground:
                self.state = "walking"
        else:
            if self.on_ground:
                self.state = "idle"
        
        # Pulo
        if (keys.up or keys.w) and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
            self.state = "jumping"
            sounds.jump.play()
        
        # Aplicar gravidade
        self.vel_y += GRAVITY
        if self.vel_y > 15:  # Velocidade máxima de queda
            self.vel_y = 18
        
        # Atualizar posição
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Verificar limites da tela
        if self.x < 0:
            self.x = 0
        elif self.x > WIDTH - self.width:
            self.x = WIDTH - self.width

        self.on_ground = False  # Assumimos que ele está no ar até verificar

        # Verifica colisão com o chão
        if self.y + self.height >= HEIGHT - 100:
            self.y = HEIGHT - 100 - self.height
            self.vel_y = 0
            self.on_ground = True

        # Verifica colisão com plataformas
        else:
            for plat in platforms:
                if (self.y + self.height >= plat.top and
                    self.y + self.height - self.vel_y <= plat.top and  # colisão vindo de cima
                    self.x + self.width > plat.left and
                    self.x < plat.right):
                    self.y = plat.top - self.height
                    self.vel_y = 0
                    self.on_ground = True
                    break
        ''''
        # Chão simples sem detecção de plataforma real
        if self.y > HEIGHT - 100:
            self.y = HEIGHT - 100
            self.vel_y = 0
            self.on_ground = True
            if self.vel_x == 0:
                self.state = "idle"
                '''
        
        # Atualizar animação baseada no estado
        if self.state == "idle":
            if self.frames != self.idle_frames:
                self.frames = self.idle_frames
                self.current_frame = 0
        elif self.state == "walking":
            if self.frames != self.walk_frames:
                self.frames = self.walk_frames
                self.current_frame = 0
        elif self.state == "jumping":
            if self.frames != self.jump_frames:
                self.frames = self.jump_frames
                self.current_frame = 0
            # Frame manual baseado na direção do pulo
            if self.vel_y < 0:
                self.current_frame = 0  # Subindo → player-jump-1
            else:
                self.current_frame = 1  # Descendo → player-jump-2

        if self.state != "jumping":
            self.update_animation()
        
        # Cooldown do tiro
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
    
    def shoot(self):
        """Cria uma bala na direção que o jogador está olhando"""
        if self.shoot_cooldown <= 0:
            direction = 1 if self.facing_right else -1
            bullet_x = self.x + (self.width if self.facing_right else 0)
            bullet_y = self.y + self.height // 2
            bullets.append(Bullet(bullet_x, bullet_y, direction))
            self.shoot_cooldown = 20  # Cooldown de 20 frames

class Enemy(AnimatedSprite):
    """Classe dos inimigos com movimento e animação"""
    def __init__(self, x, y, patrol_start, patrol_end):
        # Frames de animação do inimigo
        idle_frames = [f'slimer-idle{i}' for i in range(1, 9)]  # 8 frames idle
        move_frames = [f'slimer{i}' for i in range(1, 8)]       # 7 frames movimento
        
        super().__init__(x, y, idle_frames, 0.12)
        
        self.idle_frames = idle_frames
        self.move_frames = move_frames
        self.facing_right = True
        
        # Configurações de patrulha
        self.patrol_start = patrol_start
        self.patrol_end = patrol_end
        self.direction = 1  # 1 para direita, -1 para esquerda
        self.moving = True
        self.idle_timer = 0
        self.idle_duration = random.randint(60, 120)  # Frames para ficar parado
        
        # Vida do inimigo
        self.health = 3
        self.hit_timer = 0  # No futuro para efeito visual quando é atingido 
        
    def update(self):
        """Atualiza o inimigo"""
        # Lógica de movimento/patrulha
        if self.moving:
            self.x += self.direction * ENEMY_SPEED
            
            # Verificar limites de patrulha
            if self.x <= self.patrol_start:
                self.x = self.patrol_start
                self.direction = 1
                self.facing_right = True
                self.moving = False
                self.idle_timer = 0
            elif self.x >= self.patrol_end:
                self.x = self.patrol_end
                self.direction = -1
                self.facing_right = False
                self.moving = False
                self.idle_timer = 0
            
            # Usar frames de movimento
            if self.frames != self.move_frames:
                self.frames = self.move_frames
                self.current_frame = 0
        else:
            # Parado - usar frames idle
            if self.frames != self.idle_frames:
                self.frames = self.idle_frames
                self.current_frame = 0
            self.idle_timer += 1
            if self.idle_timer >= self.idle_duration:
                self.moving = True
                self.idle_duration = random.randint(60, 120)
        
        self.update_animation()
        
        # Reduzir timer de hit
        if self.hit_timer > 0:
            self.hit_timer -= 1
    
    def take_damage(self):
        """Inimigo recebe dano"""
        self.health -= 1
        # self.hit_timer = 15  # Efeito visual por 15 frames
        sounds.enemy_hit.play()  # Adiciona som de hit 
        return self.health <= 0  # Retorna True se morreu

''' Tiro utilizando Retangulos
class Bullet:
    """Classe das balas do jogador"""
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = BULLET_SPEED * direction
        self.width = 8
        self.height = 4
        sounds.fireball.play()
        
    def update(self):
        """Atualiza a bala"""
        self.x += self.speed
        
    def get_rect(self):
        """Retorna o retângulo de colisão"""
        return Rect(self.x, self.y, self.width, self.height)
    
    def is_off_screen(self):
        """Verifica se a bala saiu da tela"""
        return self.x < -10 or self.x > WIDTH + 10
'''
class Bullet:
    """Classe da fireball do jogador com animação"""
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y -12
        self.direction = direction
        self.speed = BULLET_SPEED * direction
        self.width = 2  # ajuste para tamanho da fireball
        self.height = 2

        # Animação
        self.facing_right = direction > 0  # flip baseado na direção
        self.frames = [f"fireball-{i}" for i in range(1, 6)]
        self.current_frame = 0
        self.animation_speed = 0.2
        self.animation_timer = 0
        
    def update(self):
        """Atualiza a bala"""
        self.x += self.speed
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
        
    def get_current_frame(self):
        """Retorna o frame atual da animação, com flip se necessário"""
        frame = self.frames[self.current_frame]
        if not self.facing_right:
            return frame + "-flip"
        return frame

    """Retorna o retângulo de colisão"""
    def get_rect(self):
        return Rect(self.x, self.y, self.width, self.height)
    
    """Verifica se a bala saiu da tela"""
    def is_off_screen(self):
        return self.x < -10 or self.x > WIDTH + 10

class Acorn(AnimatedSprite):
    """Classe para moedas(bolotas) coletaveis"""
    def __init__(self, x, y):
        frames = [f'acorn-{i}' for i in range(1, 4)]  # 3 frames de animação
        super().__init__(x, y, frames, animation_speed=0.2)
        self.width = 16
        self.height = 16
        self.collected = False

    def update(self):
        if not self.collected:
            self.update_animation()

    def get_rect(self):
        return Rect(self.x, self.y, self.width, self.height)

class Button:
    """Classe para botões clicáveis do menu"""
    def __init__(self, x, y, width, height, text, action):
        self.rect = Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        
        
    def update(self, mouse_pos):
        """Atualiza o estado do botão"""
        self.hovered = self.rect.collidepoint(mouse_pos)
        
    def click(self):
        """Executa a ação do botão"""
        if self.hovered:
            self.action()


# Instâncias do jogo
player = Player(100, HEIGHT - 100 - 32)  # chão (600 - 100) - altura
enemies = []
bullets = []
buttons = []

def init_game():
    """Inicializa o jogo"""
    global player, enemies, bullets, acorns, score, lives
    
    # Reiniciar jogador
    player = Player(100, HEIGHT - 150)

    # Resetar vidas e score
    lives = 3
    score = 0
    
    # Limpar listas
    enemies.clear()
    acorns.clear()
    # Inimigos no chão
    enemy_y_ground = HEIGHT - 100 - 32 - 6  # 600 - 100 (chão) - altura do inimigo

    # Inimigo sobre plataforma (altura da plataforma: 20px, y = 400)
    # platform_y = HEIGHT - 200
    # enemy_y_platform = platform_y - 32 - 6  # Plataforma - altura do inimigo 

    # Inimigos no chão
    enemy_y_ground = HEIGHT - 100 - 32 - 6
    enemies.append(Enemy(300, enemy_y_ground, 250, 450))
    enemies.append(Enemy(600, enemy_y_ground, 550, 700))

    # Inimigos nas plataformas
    enemy_width = 32

    # Plataforma 1 (mais baixa)
    plat1_x = 450
    plat1_y = HEIGHT - 200
    plat1_width = 200
    enemy_y1 = plat1_y - 32 - 6
    enemies.append(Enemy(plat1_x + 20, enemy_y1, plat1_x, plat1_x + plat1_width - enemy_width))

    # Plataforma 2 (mais alta)
    plat2_x = 200
    plat2_y = HEIGHT - 320
    plat2_width = 180
    enemy_y2 = plat2_y - 32 - 6
    enemies.append(Enemy(plat2_x + 20, enemy_y2, plat2_x, plat2_x + plat2_width - enemy_width))

    # Criar moedas (acorns)

    # 4 Moedas no chão
    acorns.append(Acorn(750, HEIGHT - 100 - 16))
    acorns.append(Acorn(300, HEIGHT - 100 - 16))
    acorns.append(Acorn(450, HEIGHT - 100 - 16))
    acorns.append(Acorn(600, HEIGHT - 100 - 16))

    # 2 Moedas em cada plataforma aérea
    acorns.append(Acorn(plat1_x + 40, plat1_y - 16))
    acorns.append(Acorn(plat1_x + 120, plat1_y - 16))
    acorns.append(Acorn(plat2_x + 30, plat2_y - 16))
    acorns.append(Acorn(plat2_x + 110, plat2_y - 16))
    
    #limpar balas
    bullets.clear()

def start_game():
    """Inicia o jogo"""
    global game_state
    game_state = PLAYING
    init_game()

def toggle_music():
    """Liga/desliga a música"""
    global music_enabled
    music_enabled = not music_enabled
    
    if music_enabled:
        # As linhas abaixo para controlar a música
         music.play('background_music')
         music.set_volume(0.2)
         sounds.stomp.play()  # Som de confirmação
    else:
        # A linha abaixo para parar a música
         music.stop()

def quit_game():
    """Sai do jogo"""
    quit()

def init_menu():
    """Inicializa o menu"""
    global buttons
    buttons.clear()
    
    # Criar botões do menu
    button_width = 200
    button_height = 50
    button_x = WIDTH // 2 - button_width // 2
    
    buttons.append(Button(button_x, 250, button_width, button_height,
                           "Start Game", start_game))
    buttons.append(Button(button_x, 320, button_width, button_height, 
                         f"Music {'On' if music_enabled else 'Off'}", toggle_music))
    buttons.append(Button(button_x, 390, button_width, button_height,
                           "Quit", quit_game))

def update():
    """Função principal de atualização"""
    global game_state, buttons, score, lives, instruction_timer

    if instruction_timer > 0:
        instruction_timer -= 1
    
    if game_state == MENU:
    # Desativado: atualização do botão com posição do mouse, pois não temos acesso
        for button in buttons:
            button.hovered = False  # hover só será ativado ao clicar
            
        # Atualizar texto do botão de música
        if buttons:
            buttons[1].text = f"Music {'On' if music_enabled else 'Off'}"
            
    elif game_state == PLAYING:
        player.update()

        # Atualizar inimigos
        for enemy in enemies[:]:
            enemy.update()

            # Colisão com jogador
            if player.get_rect().colliderect(enemy.get_rect()):
                lives -= 1
                # sounds.player_hit.play()  
                if lives <= 0:
                    game_state = GAME_OVER
                else:
                    # Reiniciar posição do jogador
                    player.x = 100
                    player.y = HEIGHT - 100 - 32
                    player.vel_x = 0
                    player.vel_y = 0

         # Atualizar balas
        for bullet in bullets[:]:
            bullet.update()
            
            # Remover balas que saíram da tela
            if bullet.is_off_screen():
                bullets.remove(bullet)
                continue
            
            # Verificar colisão com inimigos
            bullet_rect = bullet.get_rect()
            for enemy in enemies[:]:
                enemy_rect = enemy.get_rect()
                if bullet_rect.colliderect(enemy_rect):
                    bullets.remove(bullet)
                    if enemy.take_damage():
                        enemies.remove(enemy)
                        score += 10
                    break

        # Atualizar acorns
        for acorn in acorns:
            acorn.update()
            if not acorn.collected and player.get_rect().colliderect(acorn.get_rect()):
                acorn.collected = True
                score += 10
                sounds.coin.play()       

        # Verificar vitória: todos acorns coletados E todos inimigos derrotados
        if all(acorn.collected for acorn in acorns) and not enemies:
            game_state = GAME_OVER

def draw():
    """Função principal de desenho"""
    screen.clear()
    
    if game_state == MENU:
        # Desenhar menu
        # A linha abaixo para adicionar imagem de fundo do menu
        screen.blit('menu_background', (0, 0))
        
        # Fundo simples para o menu
        #screen.fill((30, 30, 60))
        
        # Sub-Título do jogo
        screen.draw.text("PRACTICAL TEST", center=(WIDTH//2, 220), 
                        fontsize=38, color="white")
        
        # Desenhar botões
        for button in buttons:
            color = (70, 70, 100) if button.hovered else (109, 0, 78)
            screen.draw.filled_rect(button.rect, color)
            screen.draw.rect(button.rect, "white")
            screen.draw.text(button.text, center=button.rect.center, 
                           fontsize=24, color="white")
            
    elif game_state == PLAYING:
        # Desenhar jogo
        # A linha abaixo para adicionar imagem de fundo do jogo
        screen.blit('game_background', (0, 0))
        
        screen.blit("score", (672, 0))
        # Fundo simples para o jogo
        # screen.fill((135, 206, 235))  # Azul céu
        
        screen.blit("platformer", (0, HEIGHT - 100))

        # Desenhar chão simples
        #screen.draw.filled_rect(Rect(0, HEIGHT - 100, WIDTH, 100), 
        #                        (34, 139, 34))
        
        # Desenhar plataformas areas
        screen.blit("plat_air", (450, HEIGHT - 200))
        screen.blit("plat_air", (200, HEIGHT -  320, 180, 20))

        # Plataforma chão simples
        ''''
        screen.draw.filled_rect(Rect(450, HEIGHT - 200, 200, 20), 
                                (197, 85, 9))
        screen.draw.filled_rect(Rect(200, HEIGHT - 320, 180, 20),
                                 (197, 85, 9))
        '''
        # Desenhar jogador
        # Descomente a linha abaixo para usar sprite do jogador
        # screen.blit(player.get_current_frame(), (player.x, player.y))
        
        # Desenho simples do jogador (substitua pela imagem)
        color = (0, 0, 255) if player.state == 'idle' else (0, 255, 0) if player.state == 'walk' else (255, 0, 0)  # Verde
        screen.draw.filled_rect(player.get_rect(), color)
        
        # Desenhar inimigos
        for enemy in enemies:
            # Descomente a linha abaixo para usar sprite do inimigo
            screen.blit(enemy.get_current_frame(), (enemy.x, enemy.y))
            
            # Desenho simples do inimigo 
            #color = (255, 100, 100) if enemy.hit_timer > 0 else (255, 0, 0)
            #screen.draw.filled_rect(enemy.get_rect(), color)
            
            # Mostrar vida do inimigo
            screen.draw.text(f"HP: {enemy.health}", (enemy.x, enemy.y - 15), 
                           fontsize=12, color="white")
        
        # Desenhar acorns (moedas)
        for acorn in acorns:
            if not acorn.collected:
                screen.blit(acorn.get_current_frame(), (acorn.x, acorn.y))

        # Desenhar balas
        for bullet in bullets:
            # screen.draw.filled_rect(bullet.get_rect(), (255, 255, 0))
            screen.blit(bullet.get_current_frame(), (bullet.x, bullet.y))
        
        # Desenhar UI
        if instruction_timer > 0:
            screen.draw.text("Use WASD ou Arrow Keys para mover", (10, 400), 
                            fontsize=16, color="white")
            screen.draw.text("Pressione SPACE para atirar", (10, 425), 
                            fontsize=16, color="white")
            screen.draw.text("Colete as bolotas & Destrua todos os inimigos!", (10, 450), 
                            fontsize=16, color="white")
        # UI: score e vidas
        screen.draw.text(f"Score: {score}", (700, 20), fontsize=24, color="white")
        screen.draw.text(f"Lives: {lives}", (700, 50), fontsize=24, color="white")

    elif game_state == GAME_OVER:
        #screen.fill((50, 50, 100))

        if all(acorn.collected for acorn in acorns) and not enemies:
            screen.blit("win_background", (0, 0))
            screen.draw.text("YOU WIN!", center=(WIDTH//2, HEIGHT//2 - 50),
                             fontsize=48, color="green")
        else:
            screen.blit("lose_background", (0, 0))
            screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2 - 50),
                             fontsize=48, color="red")

        screen.draw.text(f"Final Score: {score}", center=(WIDTH//2, HEIGHT//2),
                         fontsize=36, color="white")
        screen.draw.text("Click to return to menu", center=(WIDTH//2, HEIGHT//2 + 50),
                         fontsize=24, color="white")

def on_mouse_down(pos):
    """Função chamada quando o mouse é clicado"""
    global game_state
    if game_state == MENU:
        for button in buttons:
            if button.rect.collidepoint(pos):
                button.hovered = True  # ativa destaque visual
                button.click()
            else:
                button.hovered = False
    elif game_state == GAME_OVER:
        game_state = MENU
        init_menu()

def on_key_down(key):
    """Função chamada quando uma tecla é pressionada"""
    global game_state
    if game_state == PLAYING:
        if key == keys.SPACE:
            player.shoot()
        elif key == keys.ESCAPE:
            # Voltar ao menu
            game_state = MENU
            init_menu()

# Inicializar o jogo
init_menu()

# Descomente a linha abaixo para tocar música de fundo
music.play('background_music')
music.set_volume(0.2)

pgzrun.go()