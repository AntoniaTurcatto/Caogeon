import copy
import importlib.util
import sys
import types
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable

from core.model import Entity, InstancedEntity, Scene
from core.project_manager import ProjectManager

from runtime.state import EntityRuntime, SceneRuntime


class BaseLoader(ABC):
    # interface base pra qualquer loader do runtime
    @abstractmethod
    def clear_cache(self) -> None:
        pass


class ScriptLoader(BaseLoader):
    # importa scripts python em tempo de execução com cache por caminho
    # sem cache, o mesmo script seria reimportado pra cada instância da entidade

    def __init__(self) -> None:
        self._cache: dict[Path, types.ModuleType] = {}

    def clear_cache(self) -> None:
        # descarta tudo ao trocar de cena
        self._cache.clear()

    def import_script(self, script_path: Path) -> types.ModuleType:
        resolved = script_path.resolve()

        if resolved in self._cache:
            return self._cache[resolved]

        if not resolved.exists():
            raise FileNotFoundError(f"Script não encontrado: {resolved}")

        module_name = f"caogeon_script_{resolved.stem}_{len(self._cache)}"
        spec = importlib.util.spec_from_file_location(module_name, resolved)

        if spec is None or spec.loader is None:
            raise ImportError(f"Não foi possível carregar o script: {resolved}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        self._cache[resolved] = module
        return module


class SceneLoader(BaseLoader):
    # monta o SceneRuntime a partir do modelo
    #
    # pra cada entidade da cena:
    #   1. importa o script
    #   2. resolve os hooks (nome da função -> callable com ctx em closure)
    #   3. copia as variáveis do modelo pro state da instância
    #   4. registra no SceneRuntime
    # depois importa e executa o script da cena (on_load), se tiver

    def __init__(self) -> None:
        self._script_loader = ScriptLoader()

    def clear_cache(self) -> None:
        self._script_loader.clear_cache()

    def resolve_entity_hooks(self, entity: Entity, ctx: Any) -> dict[str, Callable]:
        # converte Entity.hooks {mensagem: nome_funcao} em callables reais
        # o ctx fica capturado em closure, então o hook só recebe arg quando chamado
        # esse custo acontece uma vez por cena, não a cada tick
        if not entity.hooks:
            return {}

        module = self._script_loader.import_script(entity.script_path)
        resolved: dict[str, Callable] = {}

        for message_name, function_name in entity.hooks.items():
            function = getattr(module, function_name, None)
            if function is None:
                raise AttributeError(
                    f"Função '{function_name}' não encontrada no script "
                    f"'{entity.script_path}' da entidade '{entity.unique_name}'"
                )
            resolved[message_name] = (lambda arg, _fn=function: _fn(ctx, arg))

        return resolved

    def build_entity_runtime(self, instanced: InstancedEntity, ctx: Any) -> EntityRuntime:
        # cria a EntityRuntime com hooks resolvidos e state próprio
        hooks = self.resolve_entity_hooks(instanced.entity, ctx)
        state = copy.deepcopy(instanced.entity.variables)
        return EntityRuntime(instance=instanced, hooks=hooks, state=state)

    def build_scene_runtime(self, scene: Scene, ctx: Any) -> SceneRuntime:
        # instancia todas as entidades da cena e registra no SceneRuntime
        scene_runtime = SceneRuntime()
        for instanced in scene.entities:
            entity_runtime = self.build_entity_runtime(instanced, ctx)
            scene_runtime.register_entity(entity_runtime)
        return scene_runtime

    def load_scene_script(self, scene: Scene) -> types.ModuleType | None:
        # importa o script da cena se tiver um definido
        if not scene.script_path:
            return None
        return self._script_loader.import_script(scene.script_path)


def load_project(project_path: str | Path) -> tuple[ProjectManager, Scene]:
    # ponto de entrada pra o player carregar o projeto e inicializar o runtime
    from core.managers import ProjectPaths

    project_manager = ProjectManager()
    project_manager.load(ProjectPaths(project_path))

    if project_manager.project is None:
        raise RuntimeError("project.json não encontrado")

    return project_manager, project_manager.project.initial_scene
