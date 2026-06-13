# Caogeon
Plataforma de criação de jogos que usa python como linguagem de script

## Módulos
 
### runtime/
Runtime que lê o model e executa o jogo. Expõe uma API pública que scripts customizados podem chamar. 
 
| Folder | Responsibility |
|--------|----------------|
| `api/` | Expõe métodos que scripts do usuário podem chamar |
| `loop/` | Controla tick, ordem de execução e estado|
| `loader/` | Lê o model, instancia entidades, importa scripts, resolve hooks em Callables e registra entidades nas subscriptions do SceneRuntime|
| `io/` | Funções e classes de IO internas|
 
### editor/
Ferramenta para edição do projeto, lê e escreve no model através do /project .
 
| File / Folder | Responsibility |
|---------------|----------------|
| `main_window.py` | Ponto de entrada da aplicação|
| `panels/` | Regiões UI individuais para manipular o model |
| `dialogs/` | Janelas modais para ações pontuais (novo projeto, excluir, salvar como, etc) |
 
### model/
utilizado pelo editor e pelo runtime/loader para carregar e manipular estado do projeto
| File / Folder | Responsibility |
|---------------|----------------|
|`core`| Classes base|
|`managers`| Contém os Managers para converter arquivos do project_files em entidades do core|
|`serializers`| Serializadores utilizados por managers|

### project_files/
O estado persistido de um projeto de um jogo. É manipulado pelo /model. 

| Folder | Contents |
|--------|----------|
| `assets/` | Assets do jogo em .json |
| `assets_files/` | arquivos dos assets |
| `entities/` | Definição de entidades (nome, referencia de sprites, binding de scripts customizados) |
| `scenes/` | Definição de cenas (localização de entidades, camera, etc) |
| `scripts/` | Scripts do usuário | 


### player/ 
Renderiza o jogo consumindo o runtime a cada tick disparado por ele. Não contém lógica do jogo. Também recebe input do usuário e informa ao runtime via `api/io/`. 

___ 
## Arquivos do project_files (arquivos do projeto)
### project_files/project.json
```
{
  "name": "Caogeon Demo Game",
  "engine_version": "1.0.0",
  "window": {
    "title": "Janela do Jogo",
    "width": 800,
    "height": 600,
    "target_fps": 60
  },
  "initial_scene_name": "level01"
}
```

### project_files/assets
```
{
  "unique_name": "imagem legal",
  "path": "file_inside_assets_file.jpg"
}
```

### project_files/entities
Assinatura dos hooks: def nome(ctx, arg), na qual ctx é a instancia em runtime, arg é o argumento passado pelo evento
exemplo: `ctx.state["vida"] = int(arg)`
O usuário deve ser cuidadoso ao que passa para cada evento
```
{
  "unique_name": "meu buneco",
  "sprite_name": "imagem legal",
  "width": 5,
  "height": 10,
  "script_path": "script.py",
  "variables": { "vida": 100, "velocidade": 5 },
  "hooks": {
    "on_spawn": "function within script.py",
    "on_click": "function within script.py"
  }
}
```

### project_files/scenes
```
{
  "unique_name": "level01",
  "background": "image_asset_name",
  "width": 5,
  "height": 10,
  "entities": [ 
    {
      "id":"meu buneco 1",
      "entity_name": "meu buneco",
      "x": 25,
      "y": 30
    },
    {
      "id":"meu buneco 2",
      "entity_name": "meu buneco",
      "x": 205,
      "y": 210
    }
  ]
}
```

### other folders
files to support the project itself
___ 

## Docs and api
[cageon_docs](/docs)

## Example project
[projeto exemplo](/example/docs)
