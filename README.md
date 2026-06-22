# Caogeon
A 2D game creation platform that uses Python as its scripting language

## Modules

### runtime/
Reads the model and executes the game. Exposes a public API that custom scripts can call.

| Folder | Responsibility |
|--------|----------------|
| `api/` | Exposes methods that user scripts can call |
| `loop/` | Controls tick, execution order and state |
| `loader/` | Reads the model, instantiates entities, imports scripts, resolves hooks into Callables and registers entities into SceneRuntime subscriptions |
| `io/` | Internal IO functions and classes |

### editor/
Tool for editing the project, reads and writes the model through `core/`.

| File / Folder | Responsibility |
|---------------|----------------|
| `main_window.py` | Application entry point |
| `panels/` | Individual UI regions for manipulating the model |
| `dialogs/` | Modal windows for one-off actions (new project, delete, save as, etc) |

### core/
Used by the editor and runtime to load and manipulate project state.

| File / Folder | Responsibility |
|---------------|----------------|
| `model` | Dataclasses representing project state in memory |
| `managers` | Abstract classes that Managers must implement and project file paths (`ProjectPaths`) |
| `serializers` | Serializers and parsers. Serializers and Serializing strategies must be implemented here, parsers within it's managers file |
| `registers` | `Registry[T]`: maps `unique_name -> instance`, shared between managers for reference resolution |
| `asset_manager` | Asset manager and parser |
| `entity_manager` | Entity manager and parser |
| `scene_manager` | Scene and instanced entity manager and parser |
| `project_manager` | Orchestrates load/save across all managers and parses `project.json` |

### project stucture:
Persisted state of a game project. Manipulated by `core/` managers.

| Folder | Contents |
|--------|----------|
| `assets/` | Game assets as `.json` |
| `assets_files/` | Physical asset files |
| `entities/` | Entity definitions (name, sprite reference, variables, hooks) |
| `scenes/` | Scene definitions (background, instanced entities and their positions) |
| `scripts/` | User Python scripts |

### player/
Renders the game by consuming the runtime at each tick. Contains no game logic. Receives user input and forwards it to the runtime via `api/io/`.

---

## project_files format

### project_files/project.json
```json
{
  "name": "Caogeon Demo Game",
  "engine_version": "1.0.0",
  "window": {
    "title": "Game Window",
    "width": 800,
    "height": 600,
    "target_fps": 60
  },
  "initial_scene_name": "level01"
}
```

### project_files/assets/
```json
{
  "unique_name": "cool_image",
  "path": "assets_files/cool_image.jpg"
}
```

### project_files/entities/
All runtime communication with an entity is done by emitting a named message. The engine emits messages on the hooks declared by the entity, calling the corresponding function in the script.

Hook signature: `def name(ctx, arg)`, where `ctx` is the runtime instance and `arg` is the argument passed by the event.

Example: `ctx.state["health"] = int(arg)`

```json
{
  "unique_name": "my_character",
  "sprite_name": "cool_image",
  "width": 5,
  "height": 10,
  "script_path": "script.py",
  "variables": { "health": 100, "speed": 5 },
  "hooks": {
    "on_spawn": "initialize",
    "on_click": "on_clicked"
  }
}
```

### project_files/scenes/
scenes scripts are inside project_file/scenes/scripts
```json
{
  "unique_name": "level01",
  "background": "cool_image",
  "entities": [
    {
      "id": "my_character_1",
      "entity_name": "my_character",
      "x": 25,
      "y": 30
    },
    {
      "id": "my_character_2",
      "entity_name": "my_character",
      "x": 205,
      "y": 210
    }
  ],
  "script_path": "level01.py"
}
```

### other folders
Project support files (configuration, metadata, etc).

---

## Docs and API
[caogeon_docs](/docs)

## Example project
[example project](/example)
