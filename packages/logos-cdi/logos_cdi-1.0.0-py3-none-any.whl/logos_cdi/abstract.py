from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Mapping, Iterable, Any, Self


class AbstractContainer(ABC):

    @abstractmethod
    def has(self, name: str, context: Optional[AbstractContext] = None) -> bool:
        ...
    
    @abstractmethod
    def get(self, name: str, context: Optional[AbstractContext] = None) -> Any:
        ...
    
    @abstractmethod
    def resources(self, context: Optional[AbstractContext] = None) -> Mapping[str, AbstractResource]:
        ...


class AbstractResource(ABC):

    @abstractmethod
    def resolve(self, context: AbstractContext, name: str = 'anonymous'):
        ...


class AbstractContext(AbstractContainer):

    @abstractmethod
    def nested(self, container: AbstractContainer) -> AbstractContext:
        ...
    
    @abstractmethod
    def children(self) -> Iterable[AbstractContext]:
        ...
    
    @abstractmethod
    def parent(self) -> Optional[AbstractContext]:
        ...


class AbstractReference(ABC):

    @abstractmethod
    def get(self, context: AbstractContext):
        ...


class ParentReference(AbstractReference):
    pass


class AbstractRegistry[T](ABC):

    @abstractmethod
    def register(self, name: str, _: T) -> Self:
        ...
    
    @abstractmethod
    def all(self) -> Mapping[str, T]:
        ...
    

