from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable

from core.model import InstancedEntity

# hook resolvido: def nome(ctx, arg) -> None capturado em closure pelo loader
HookCallable = Callable[[Any], None]


class RuntimeObject(ABC):
    # base pra qualquer coisa que recebe mensagem no runtime
    @abstractmethod
    def send_message(self, message: str, arg: Any = None) -> None:
        pass


@dataclass
class EntityRuntime(RuntimeObject):
    # estado de uma entidade enquanto o jogo tá rodando
    # separado do modelo pra cada instância ter seus próprios valores

    instance: InstancedEntity
    hooks: dict[str, HookCallable] = field(default_factory=dict)
    state: dict[str, Any] = field(default_factory=dict)  # cópia das variáveis do modelo

    # visual
    visible: bool = True
    z_index: int = 0
    rotation: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0
    flip_h: bool = False
    flip_v: bool = False

    # física simples, aplicada pelo game loop a cada tick
    velocity_x: float = 0.0
    velocity_y: float = 0.0

    @property
    def id(self) -> str:
        return self.instance.id

    @property
    def entity_name(self) -> str:
        return self.instance.entity.unique_name

    @property
    def x(self) -> int:
        return self.instance.x

    @x.setter
    def x(self, value: int) -> None:
        self.instance.x = value

    @property
    def y(self) -> int:
        return self.instance.y

    @y.setter
    def y(self, value: int) -> None:
        self.instance.y = value

    @property
    def width(self) -> int:
        return self.instance.entity.width

    @property
    def height(self) -> int:
        return self.instance.entity.height

    def send_message(self, message: str, arg: Any = None) -> None:
        # chama o hook se a entidade tiver um pra essa mensagem, senão ignora
        hook = self.hooks.get(message)
        if hook is not None:
            hook(arg)


class SceneRuntime(RuntimeObject):
    # gerencia as entidades ativas da cena e quem tá inscrito em qual mensagem
    #
    # quando o kael e a mira têm hook "on_tick" mas a porta não tem,
    # o broadcast("on_tick") chama só eles dois, sem passar pela porta

    def __init__(self) -> None:
        self.entities: dict[str, EntityRuntime] = {}           # id -> entidade
        self.subscriptions: dict[str, list[EntityRuntime]] = {}  # mensagem -> inscritos

    def register_entity(self, entity: EntityRuntime) -> None:
        # adiciona na cena e inscreve nas mensagens que ela trata
        self.entities[entity.id] = entity
        for message in entity.hooks:
            self.subscriptions.setdefault(message, []).append(entity)

    def unregister_entity(self, entity_id: str) -> None:
        # remove da cena e de todas as inscrições
        entity = self.entities.pop(entity_id, None)
        if entity is None:
            return
        for subscribers in self.subscriptions.values():
            if entity in subscribers:
                subscribers.remove(entity)

    def get_entity(self, entity_id: str) -> EntityRuntime | None:
        return self.entities.get(entity_id)

    def send_message(self, message: str, arg: Any = None) -> None:
        # implementação do RuntimeObject, só repassa pra broadcast
        self.broadcast(message, arg)

    def send_message_to(self, entity_id: str, message: str, arg: Any = None) -> None:
        # manda pra uma entidade específica pelo id
        entity = self.entities.get(entity_id)
        if entity is not None:
            entity.send_message(message, arg)

    def broadcast(self, message: str, arg: Any = None) -> None:
        # manda a mensagem só pra quem tá inscrito nela
        for entity in self.subscriptions.get(message, []):
            entity.send_message(message, arg)
