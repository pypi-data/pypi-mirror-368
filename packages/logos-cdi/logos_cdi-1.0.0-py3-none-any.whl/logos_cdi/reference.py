from logos_cdi.abstract import AbstractReference, AbstractRegistry, AbstractContext


class Reference(AbstractReference):

    def __init__(self, resource_name: str):
        super().__init__()
        self.resource_name = resource_name
    
    def get(self, context):
        return context.get(self.resource_name)

class Parent(AbstractReference):

    def __init__(self, resource_name: str):
        super().__init__()
        self.resource_name = resource_name
    
    def get(self, context):
        parent = context.parent()
        return parent.get(self.resource_name) if parent.has(self.resource_name) and parent is not None else None

class Decorated(AbstractReference):

    def __init__(self, resource_name: str, current_context: AbstractContext, legacy: bool = False):
        super().__init__()
        self.resource_name = resource_name
        self.current_context = current_context
        self.legacy = legacy
    
    def get(self, context):
        return self.current_context.get(self.resource_name, context if not self.legacy else self.current_context)

class Context(AbstractReference):

    def get(self, context):
        return context
    

class AllRegisteredReference(AbstractReference):

    def __init__(self, registry_name: str, lazy: bool = False):
        super().__init__()
        self.registry_name = registry_name
        self.lazy = lazy
    
    def get(self, context):
        registry: AbstractRegistry[AbstractReference] = context.get(self.registry_name)
        return {
            name: reference.get(context) if not self.lazy else lambda: reference.get(context)
            for name, reference in registry.all().items()
        }