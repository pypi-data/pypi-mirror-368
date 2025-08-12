from typing import Dict, Type, Optional, List, Any

from wexample_app.common.service.service_mixin import ServiceMixin
from wexample_helpers.service.registry import Registry


class ServiceRegistry(Registry[Type[ServiceMixin]]):
    """Registry for managing services of type ServiceMixin."""
    _service_instances: Dict[str, ServiceMixin] = {}
    container: Any  # Will be ServiceMixinContainer at runtime

    def register(self, key: str, service_class: Type[ServiceMixin]) -> None:
        """Register a service class in the registry."""
        self._items[key] = service_class

    def get(self, key: str | Type[ServiceMixin], **kwargs) -> Optional[ServiceMixin]:
        """
        Retrieve a service by its key. Instantiates the service if it doesn't exist.
        Additional kwargs are passed to the service constructor.
        """
        # If key is a class, use its name
        if isinstance(key, type):
            key = key.get_snake_short_class_name()

        # Return existing instance if already instantiated
        if key in self._service_instances:
            return self._service_instances[key]

        # Get service class and create new instance if exists
        service_class = self._items.get(key)
        if service_class:
            # Rebuild model if it's a Pydantic model using HasClassDependencies mixin.
            if hasattr(service_class, 'import_dependencies_and_rebuild'):
                service_class.import_dependencies_and_rebuild()
            # Rebuild model if it's a Pydantic model
            elif hasattr(service_class, 'model_rebuild'):
                service_class.model_rebuild()

            # Create instance with kernel
            instance = service_class(**kwargs).setup()
            self._service_instances[key] = instance
            return instance

        self._raise_error_if_expected(key, None)

        return None

    def instantiate_all(self, **kwargs) -> Dict[str, ServiceMixin]:
        """
        Instantiate all registered services with the given kwargs.
        Returns a dictionary of service instances keyed by their names.
        """
        for key, service_class in self._items.items():
            if key not in self._service_instances:
                self.get(key, **kwargs)
        return self.all_instances()

    def get_class(self, key: str) -> Optional[Type[ServiceMixin]]:
        """Get the service class without instantiating it."""
        return self._items.get(key)

    def all_classes(self) -> List[Type[ServiceMixin]]:
        """Return all registered service classes."""
        return list(self._items.values())

    def all_instances(self) -> Dict[str, ServiceMixin]:
        """Return all instantiated services."""
        return self._service_instances.copy()

    def get_all(self) -> Dict[str, ServiceMixin]:
        """Get all instantiated services."""
        return self._service_instances
