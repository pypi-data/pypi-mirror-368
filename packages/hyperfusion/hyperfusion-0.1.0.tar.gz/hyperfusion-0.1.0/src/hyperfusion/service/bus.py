import asyncio
from dataclasses import field, dataclass
from typing import Dict, Type, Any, List, Callable, Awaitable, TypeVar

T = TypeVar('T')

@dataclass
class Bus:
    _listeners: Dict[Type[Any], List[Callable[[Any], Awaitable[None]]]] = field(default_factory=dict)

    def subscribe(self, event_type: Type[T], listener: Callable[[T], Awaitable[None]]) -> None:
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)

    def unsubscribe(self, event_type: Type[T], listener: Callable[[T], Awaitable[None]]) -> None:
        if event_type in self._listeners:
            self._listeners[event_type].remove(listener)

    async def publish(self, event: T) -> None:
        event_type = type(event)
        if event_type in self._listeners:
            tasks = [listener(event) for listener in self._listeners[event_type]]
            await asyncio.gather(*tasks)