# Caogeon
Plataforma de criação de jogos baseado em relacionamento, escolhas e interações

## Módulos
 
### `engine/` 
Runtime que lê o model e executa o jogo. Expõe uma API pública que scripts customizados podem chamar. 
 
| Folder | Responsibility |
|--------|----------------|
| `api/` | Expõe métodos que scripts do usuário podem chamar |
| `loop/` | Controla tick, ordem de execução e estado|
| `loader/` | Lê o model, instancia entidadaes, liga scripts e registra seus callbacks na API|
 
---
 
### `editor/`
Ferramenta para edição do projeto, lê e escreve no model.
 
| File / Folder | Responsibility |
|---------------|----------------|
| `main_window.py` | Ponto de entrada da aplicação|
| `panels/` | Regiões UI individuais para manipular o model |
| `dialogs/` | Janelas modais para ações pontuais (novo projeto, excluir, salvar como, etc) |
 
---
 
### `model/`
O estado persistido de um projeto de um jogo. Contém somente dados, sem lógica de execução. É manipulado pelo editor e uutilizado pela engine no loader. 

| Folder | Contents |
|--------|----------|
| `assets/` | Assets do jogo |
| `entities/` | Definição de entidades (nome, referencia de sprites, binding de scripts customizados) |
| `scenes/` | Definição de cenas (localização de entidades, camera, etc) |
| `scripts/` | Scripts do usuário |
 
---
 
### `player/`
 
Renderiza o jogo consumindo a engine a cada tick disparado por ela. Não contém lógica do jogo. Recebe input do usuário e informa a engine via `api/io/`.
 
---


--- 
# Projeto exemplo
## Kael, um lobo antropomórfico
acorda preso dentro da masmorra Vhaldris sem saber como chegou ali. Durante sua tentativa de escapar, ele encontra outros personagens presos na dungeon, como Mira, Brunn e Lyra, que ajudam o jogador a resolver puzzles e desbloquear novas áreas. Ao longo da história, o jogador precisa tomar decisões, resolver desafios e criar amizade com os personagens para conseguir chegar até a saída final da masmorra

## Mira
Uma gatinha muito inteligente e rápida. Conhece armadilhas e portas secretas da masmorra. No começo não confia em ninguém.
## Brunn
Um urso grande e forte que vive há muito tempo dentro da dungeon. Conhece vários caminhos antigos do lugar.
## Lyra
Uma raposa vermelha ligada à magia da dungeon. Ela consegue sentir presenças estranhas e caminhos invisíveis
