from typing import Any, Optional, List, Type, cast, TYPE_CHECKING

from wexample_helpers.service.mixins.registry_container_mixin import RegistryContainerMixin

if TYPE_CHECKING:
    from wexample_app.service.service_registry import ServiceRegistry
    from wexample_helpers.service.registry import Registry


class ServiceContainerMixin(RegistryContainerMixin):
    """Container for managing multiple service registries."""

    def _get_registry_class_type(self) -> Type["ServiceRegistry"]:
        from wexample_app.service.service_registry import ServiceRegistry
        return ServiceRegistry

    def register_service(self, registry_name: str, key: str, service: Any) -> "Registry":
        """Register a service in a specific registry."""
        return self.register_item(registry_name, key, service)

    def register_services(self, registry_name: str, services: List[Any]) -> "Registry":
        """Register multiple services at once in a specific registry."""
        return self.register_items(registry_name, services)

    def get_service(self, registry_name: str, key: str) -> Optional[Any]:
        """Retrieve a service from a specific registry by its key."""
        return self.get_item(registry_name, key)

    def get_service_registry(self, registry_name: str) -> "ServiceRegistry":
        from wexample_app.service.service_registry import ServiceRegistry

        return cast(ServiceRegistry, self.get_registry(registry_name))
