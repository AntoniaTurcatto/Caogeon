# Caogeon
Plataforma de criação de jogos que usa python como linguagem de script

## Módulos
 
### runtime/
Runtime que lê o model e executa o jogo. Expõe uma API pública que scripts customizados podem chamar. 
 
| Folder | Responsibility |
|--------|----------------|
| `api/` | Expõe métodos que scripts do usuário podem chamar |
| `loop/` | Controla tick, ordem de execução e estado|
| `loader/` | Lê o model, instancia entidades, liga scripts e registra seus callbacks na API|
| `io/` | Funções e classes de IO internas|
 
### editor/
Ferramenta para edição do projeto, lê e escreve no model.
 
| File / Folder | Responsibility |
|---------------|----------------|
| `main_window.py` | Ponto de entrada da aplicação|
| `panels/` | Regiões UI individuais para manipular o model |
| `dialogs/` | Janelas modais para ações pontuais (novo projeto, excluir, salvar como, etc) |
 
### model/
O estado persistido de um projeto de um jogo. É manipulado pelo editor e utilizado pelo submódulo runtime/loader. 

| Folder | Contents |
|--------|----------|
| `assets/` | Assets do jogo |
| `entities/` | Definição de entidades (nome, referencia de sprites, binding de scripts customizados) |
| `scenes/` | Definição de cenas (localização de entidades, camera, etc) |
| `scripts/` | Scripts do usuário | 

### player/ 
Renderiza o jogo consumindo o runtime a cada tick disparado por ele. Não contém lógica do jogo. Também recebe input do usuário e informa ao runtime via `api/io/`. 

[projeto exemplo](/example/docs)
