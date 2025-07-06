# Platformer Fox - Game - Projeto em Pygame Zero

## 📌 Sobre o Projeto
- Este projeto é um jogo de plataforma 2D desenvolvido com a biblioteca Pygame Zero, utilizando Python como linguagem principal. O objetivo é oferecer uma experiência interativa onde o jogador controla um personagem que pode se mover, pular e atirar projéteis animados para derrotar inimigos.

- O projeto foi desenvolvido com foco didático, buscando aplicar conceitos de:

  - Lógica de programação em Python;
  - Orientação a objetos
  - Animações quadro a quadro (sprites com múltiplos frames);
  - Detecção de colisão;
  - Estados de jogo (MENU, PLAYING, GAME_OVER);
  - Interface básica com botões e instruções na tela.
---

## 🎮 Como Jogar

- Use **W A S D** ou as **setas** para se mover.
- Pressione **ESPAÇO** para atirar.
- Derrote todos os inimigos para vencer.
- Se colidir com um inimigo, volta para posição inicial e ao perder as 3 vidas o jogo termina.
- A pontuação aumenta ao eliminar inimigos e coletar as "nozes"(moedas).

## 🖼️ Recursos Visuais

- **Sprites animados** para o jogador, inimigos e projéteis.
- Fundo do jogo muda ao **vencer** ou **perder**.
- Texto com instruções some após 10 segundos.

## 🚀 Game_State
- O jogo possui 3 estados: MENU, PLAYING, GAME_OVER. Sendo no game over que ocorre a verificação tanto de vitoria como derrota.

## 📁 Estrutura do Projeto
 - Algumas imagens devem estar na pasta images/ com nomes específicos, assim como sounds e music.
- /meu_projeto/
- │
- ├── gamefox.py # Código principal do jogo
- ├── README.md # (Este arquivo)
- └── images/ # Pasta com todos os sprites
- ├──────── fireball-1.png
- ├──────── fireball-1-flip.png
- ├──────── win_background.png
- └──────── ...

## ▶️ Como Executar

1. Instale o Python (versão 3.10 ou superior).
2. Instale o Pygame Zero:

```bash
pip install pgzero
```

- Execute o jogo com:
```bash
pgzrun gamefox.py 
```

✏️ Créditos e Observações
- Jogo feito para fins didáticos.
- Código estruturado com orientação a objetos (classes AnimatedSprite, Player, Enemy, Bullet, Acorn, Button).
- Para usar o sprites do player principal deve comentar a linha 601 e comntar a 604 e 605
- Para ter os assets completos acessas: https://ansimuz.itch.io/sunny-land-pixel-game-art
- Foram realizadas modificações dos sprites em algumas partes do jogo
- Musica Principal do BoxCat Games: https://freemusicarchive.org/music/BoxCat_Games

🚀 Melhorias Futuras (sugestões)
- Continuar sistema de animação do inimigo ao receber dano da fireball.
- Adicionar animações ao player.
- Incluir fases com níveis de dificuldade, realizando a transição de nivel através da porta que já está nos arquivos do projeto.
- Menu de pausa e opções como aumentar ou diminuir o volume da musica principal. 