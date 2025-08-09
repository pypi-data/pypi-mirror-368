from logos_cdi.abstract import AbstractContext, AbstractContainer, AbstractResource
from logos_cdi.error import ResourceNotFoundException
from typing import Optional, Iterable, Mapping, Any
from weakref import WeakSet

class Context(AbstractContext):

    def __init__(self, container: AbstractContainer, parent: Optional[AbstractContext] = None):
        super().__init__()
        self._container = container
        self._parent = parent
        self._children = WeakSet()
    
    def has(self, name: str, context: Optional[AbstractContext] = None) -> bool:
        return self._container.has(name, context or self) or self._parent is not None and self._parent.has(name, context or self)
    
    def get(self, name, context = None) -> Any:    
        if self._container.has(name, context or self):
            return self._container.get(name, context or self)
        if self._parent is not None and self._parent.has(name, context or self):
            return self._parent.get(name, context or self)
        raise ResourceNotFoundException(name, self)
    
    def resources(self, context: Optional[AbstractContext] = None) -> Mapping[str, AbstractResource]:
        resource = {
            resource_name: resource
            for resource_name, resource in self._container.resources(context or self).items()
        }
        if self._parent is not None:
            resource.update(self._parent.resources(context or self))
        return resource
    
    def children(self) -> Iterable[AbstractContext]:
        return list(self.children)
    
    def parent(self) -> Optional[AbstractContext]:
        return self._parent
    
    def nested(self, container: AbstractContainer) -> AbstractContext:
        nested = Context(container, self)
        self._children.add(nested)
        return nested

    