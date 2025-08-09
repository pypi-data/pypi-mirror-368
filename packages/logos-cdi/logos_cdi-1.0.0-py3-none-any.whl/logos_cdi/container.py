from logos_cdi.abstract import AbstractContainer, AbstractResource
from logos_cdi.error import ResourceNotFoundException
from typing import Mapping


class Container(AbstractContainer):

    def __init__(self, resources: Mapping[str, AbstractResource]):
        super().__init__()
        self._resources = resources

    def has(self, name, context = None):
        return name in self._resources.keys()
    
    def get(self, name, context = None):
        resource = self._resources.get(name)
        if resource is not None:
            return resource.resolve(context, name)
        raise ResourceNotFoundException(name, self)
    
    def resources(self, context):
        return {
            resource_name: resource
            for resource_name, resource in self._resources.items()
        }
