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
| `assets/` | Assets do jogo em .json |
| `entities/` | Definição de entidades (nome, referencia de sprites, binding de scripts customizados) |
| `scenes/` | Definição de cenas (localização de entidades, camera, etc) |
| `scripts/` | Scripts do usuário | 
| `assets_bin/` | arquivos dos assets|

### player/ 
Renderiza o jogo consumindo o runtime a cada tick disparado por ele. Não contém lógica do jogo. Também recebe input do usuário e informa ao runtime via `api/io/`. 

___ 
## Arquivos do model (arquivos do projeto)
### model/project.json
```
{
  "project_name": "Caogeon Demo Game",
  "engine_version": "1.0.0",
  "window": {
    "title": "Janela do Jogo",
    "width": 800,
    "height": 600,
    "target_fps": 60
  },
  "initial_scene": "level01"
}
```

### model/assets
```
{
  "unique_name": "imagem legal",
  "path": "file_inside_assets_bin.jpg"
}
```

### model/entities
```
{
  "unique_name": "meu buneco",
  "sprite_name": "imagem legal",
  "width": 5,
  "height": 10,
  "script_path": "file_inside_scripts.py",
  "events": [
    {
      "trigger": "on_spawn",
      "handler": "inicializar_personagem"
    },
    {
      "trigger": "on_click",
      "handler": "ao_clicar_no_boneco"
    },
    {
      "trigger": "on_collision",
      "handler": "processar_colisao"
    }
  ]
}
```

### scenes
```
  "scene_unique_name": "level01",
  "background": "image_asset_name",
  "width": 5,
  "height": 10,
  "entities": [ 
    {
      "id":"meu buneco 1",
      "entity_name": "meu buneco",
      "relative_x": 25,
      "relative_y": 30
    },
    {
      "id":"meu buneco 2",
      "entity_name": "meu buneco",
      "relative_x": 25,
      "relative_y": 30
    }
  ]
```

### other folders
files to support the model itself
___ 

[projeto exemplo](/example/docs)
