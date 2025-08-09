# this_file: external/int_folders/d361/src/d361/utils/dependency_injection.py
"""
Dependency Injection System - Container and decorators for service management.

This module provides a lightweight dependency injection framework for the d361
library, enabling clean architecture patterns with automatic service resolution,
lifecycle management, and dependency graph validation.
"""

from __future__ import annotations

import inspect
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, get_origin, get_args

from loguru import logger

T = TypeVar("T")


class ServiceLifecycle(str, Enum):
    """Service lifecycle management modes."""
    SINGLETON = "singleton"      # Single instance for the lifetime of the container
    TRANSIENT = "transient"      # New instance for each resolution
    SCOPED = "scoped"           # Single instance per scope (e.g., per request)


class ServiceError(Exception):
    """Base exception for dependency injection operations."""
    pass


class ServiceNotFoundError(ServiceError):
    """Exception raised when a requested service is not registered."""
    pass


class CircularDependencyError(ServiceError):
    """Exception raised when circular dependencies are detected."""
    pass


class ServiceRegistrationError(ServiceError):
    """Exception raised when service registration fails."""
    pass


@dataclass
class ServiceDescriptor:
    """Descriptor for registered services."""
    service_type: Type
    implementation: Union[Type, Callable, Any]
    lifecycle: ServiceLifecycle
    factory: Optional[Callable] = None
    singleton_instance: Optional[Any] = None
    dependencies: List[Type] = field(default_factory=list)
    lazy: bool = True
    
    def __post_init__(self):
        """Extract dependencies from implementation if it's a class."""
        if inspect.isclass(self.implementation) and not self.dependencies:
            self.dependencies = self._extract_dependencies(self.implementation)
    
    def _extract_dependencies(self, cls: Type) -> List[Type]:
        """Extract constructor dependencies from a class."""
        dependencies = []
        try:
            signature = inspect.signature(cls.__init__)
            for name, param in signature.parameters.items():
                if name == "self":
                    continue
                if param.annotation != inspect.Parameter.empty:
                    # Handle typing constructs like Optional[SomeClass] 
                    annotation = param.annotation
                    origin = get_origin(annotation)
                    if origin is Union:
                        # Handle Optional (Union[T, None])
                        args = get_args(annotation)
                        if len(args) == 2 and type(None) in args:
                            annotation = next(arg for arg in args if arg is not type(None))
                    dependencies.append(annotation)
        except Exception as e:
            logger.warning(f"Failed to extract dependencies from {cls}: {e}")
        return dependencies


class ServiceScope:
    """Service scope for managing scoped service lifetimes."""
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.instances: Dict[Type, Any] = {}
        self.created_at = None
    
    def get_instance(self, service_type: Type) -> Optional[Any]:
        """Get scoped instance if it exists."""
        return self.instances.get(service_type)
    
    def set_instance(self, service_type: Type, instance: Any) -> None:
        """Store scoped instance."""
        self.instances[service_type] = instance
        
    def clear(self) -> None:
        """Clear all scoped instances."""
        self.instances.clear()


class ServiceContainer:
    """
    Dependency injection container with service lifecycle management.
    
    Features:
    - Service registration with multiple lifecycle modes
    - Automatic dependency resolution
    - Circular dependency detection
    - Scoped service management
    - Factory function support
    - Thread-safe operations
    """
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._resolving: set = set()  # Track services currently being resolved
        self._lock = threading.RLock()
        self._scopes: Dict[str, ServiceScope] = {"default": ServiceScope("default")}
        self._current_scope = "default"
        
        # Register self
        self.register_singleton(ServiceContainer, self)
        
    def register_singleton(
        self, 
        service_type: Type[T], 
        implementation: Union[Type[T], T, Callable[..., T]], 
        factory: Optional[Callable] = None
    ) -> ServiceContainer:
        """
        Register a service with singleton lifecycle.
        
        Args:
            service_type: The service interface/type to register
            implementation: Class, instance, or factory function
            factory: Optional factory function for creating instances
            
        Returns:
            Self for method chaining
        """
        return self._register(service_type, implementation, ServiceLifecycle.SINGLETON, factory)
    
    def register_transient(
        self, 
        service_type: Type[T], 
        implementation: Union[Type[T], Callable[..., T]], 
        factory: Optional[Callable] = None
    ) -> ServiceContainer:
        """
        Register a service with transient lifecycle.
        
        Args:
            service_type: The service interface/type to register
            implementation: Class or factory function
            factory: Optional factory function for creating instances
            
        Returns:
            Self for method chaining
        """
        return self._register(service_type, implementation, ServiceLifecycle.TRANSIENT, factory)
    
    def register_scoped(
        self, 
        service_type: Type[T], 
        implementation: Union[Type[T], Callable[..., T]], 
        factory: Optional[Callable] = None
    ) -> ServiceContainer:
        """
        Register a service with scoped lifecycle.
        
        Args:
            service_type: The service interface/type to register
            implementation: Class or factory function
            factory: Optional factory function for creating instances
            
        Returns:
            Self for method chaining
        """
        return self._register(service_type, implementation, ServiceLifecycle.SCOPED, factory)
    
    def _register(
        self, 
        service_type: Type[T], 
        implementation: Union[Type[T], T, Callable[..., T]], 
        lifecycle: ServiceLifecycle, 
        factory: Optional[Callable] = None
    ) -> ServiceContainer:
        """Internal registration method."""
        with self._lock:
            if service_type in self._services:
                logger.warning(f"Service {service_type} already registered, overriding")
            
            # If implementation is already an instance, treat as singleton
            if not inspect.isclass(implementation) and not callable(implementation):
                if lifecycle != ServiceLifecycle.SINGLETON:
                    logger.warning(f"Instance provided for {service_type}, forcing singleton lifecycle")
                    lifecycle = ServiceLifecycle.SINGLETON
                
                descriptor = ServiceDescriptor(
                    service_type=service_type,
                    implementation=implementation,
                    lifecycle=lifecycle,
                    factory=factory,
                    singleton_instance=implementation,
                )
            else:
                descriptor = ServiceDescriptor(
                    service_type=service_type,
                    implementation=implementation,
                    lifecycle=lifecycle,
                    factory=factory,
                )
            
            self._services[service_type] = descriptor
            logger.debug(f"Registered service {service_type} with {lifecycle} lifecycle")
            
        return self
    
    def resolve(self, service_type: Type[T]) -> T:
        """
        Resolve a service instance.
        
        Args:
            service_type: The service type to resolve
            
        Returns:
            Service instance
            
        Raises:
            ServiceNotFoundError: If service is not registered
            CircularDependencyError: If circular dependencies detected
        """
        return self._resolve(service_type, set())
    
    def _resolve(self, service_type: Type[T], resolving_stack: set) -> T:
        """Internal resolution method with circular dependency detection."""
        # Check for circular dependencies
        if service_type in resolving_stack:
            chain = " -> ".join([str(t) for t in resolving_stack] + [str(service_type)])
            raise CircularDependencyError(f"Circular dependency detected: {chain}")
        
        with self._lock:
            descriptor = self._services.get(service_type)
            if not descriptor:
                raise ServiceNotFoundError(f"Service {service_type} is not registered")
            
            # Handle different lifecycle modes
            if descriptor.lifecycle == ServiceLifecycle.SINGLETON:
                if descriptor.singleton_instance is not None:
                    return descriptor.singleton_instance
                    
            elif descriptor.lifecycle == ServiceLifecycle.SCOPED:
                current_scope = self._scopes[self._current_scope]
                instance = current_scope.get_instance(service_type)
                if instance is not None:
                    return instance
            
            # Create new instance
            resolving_stack.add(service_type)
            try:
                instance = self._create_instance(descriptor, resolving_stack)
                
                # Store instance based on lifecycle
                if descriptor.lifecycle == ServiceLifecycle.SINGLETON:
                    descriptor.singleton_instance = instance
                elif descriptor.lifecycle == ServiceLifecycle.SCOPED:
                    current_scope = self._scopes[self._current_scope]
                    current_scope.set_instance(service_type, instance)
                    
                logger.debug(f"Created instance of {service_type} with {descriptor.lifecycle} lifecycle")
                return instance
                
            finally:
                resolving_stack.remove(service_type)
    
    def _create_instance(self, descriptor: ServiceDescriptor, resolving_stack: set) -> Any:
        """Create a new service instance."""
        # Use factory if provided
        if descriptor.factory:
            factory_args = self._resolve_dependencies(descriptor.factory, resolving_stack)
            return descriptor.factory(**factory_args)
        
        # Use implementation directly
        implementation = descriptor.implementation
        
        # If it's already an instance, return it
        if not inspect.isclass(implementation) and not callable(implementation):
            return implementation
        
        # If it's a factory function
        if callable(implementation) and not inspect.isclass(implementation):
            factory_args = self._resolve_dependencies(implementation, resolving_stack)
            return implementation(**factory_args)
        
        # If it's a class, instantiate it
        if inspect.isclass(implementation):
            constructor_args = self._resolve_dependencies(implementation.__init__, resolving_stack)
            return implementation(**constructor_args)
        
        raise ServiceRegistrationError(f"Cannot create instance from {implementation}")
    
    def _resolve_dependencies(self, func: Callable, resolving_stack: set) -> Dict[str, Any]:
        """Resolve dependencies for a function or constructor."""
        dependencies = {}
        try:
            signature = inspect.signature(func)
            for name, param in signature.parameters.items():
                if name == "self":
                    continue
                    
                if param.annotation != inspect.Parameter.empty:
                    # Try to resolve the dependency
                    dependency_type = param.annotation
                    
                    # Handle typing constructs like Optional[SomeClass]
                    origin = get_origin(dependency_type)
                    if origin is Union:
                        args = get_args(dependency_type)
                        if len(args) == 2 and type(None) in args:
                            # Optional dependency
                            dependency_type = next(arg for arg in args if arg is not type(None))
                            try:
                                dependencies[name] = self._resolve(dependency_type, resolving_stack)
                            except ServiceNotFoundError:
                                dependencies[name] = None
                            continue
                    
                    # Required dependency
                    dependencies[name] = self._resolve(dependency_type, resolving_stack)
                elif param.default != inspect.Parameter.empty:
                    # Use default value
                    dependencies[name] = param.default
                    
        except Exception as e:
            logger.error(f"Failed to resolve dependencies for {func}: {e}")
            raise ServiceRegistrationError(f"Cannot resolve dependencies for {func}: {e}")
        
        return dependencies
    
    def is_registered(self, service_type: Type) -> bool:
        """Check if a service type is registered."""
        return service_type in self._services
    
    def get_registered_services(self) -> List[Type]:
        """Get list of all registered service types."""
        return list(self._services.keys())
    
    @contextmanager
    def scope(self, scope_name: str = None):
        """
        Create a new service scope context manager.
        
        Args:
            scope_name: Name for the scope, auto-generated if None
        """
        if scope_name is None:
            scope_name = f"scope_{len(self._scopes)}"
            
        old_scope = self._current_scope
        self._scopes[scope_name] = ServiceScope(scope_name)
        self._current_scope = scope_name
        
        try:
            yield self._scopes[scope_name]
        finally:
            # Cleanup scoped instances
            if scope_name in self._scopes:
                self._scopes[scope_name].clear()
                del self._scopes[scope_name]
            self._current_scope = old_scope
    
    def clear_scope(self, scope_name: str = None) -> None:
        """Clear instances in a specific scope."""
        scope_name = scope_name or self._current_scope
        if scope_name in self._scopes:
            self._scopes[scope_name].clear()


# Global container instance
_container: Optional[ServiceContainer] = None
_container_lock = threading.Lock()


def get_container() -> ServiceContainer:
    """Get the global service container instance."""
    global _container
    if _container is None:
        with _container_lock:
            if _container is None:
                _container = ServiceContainer()
    return _container


def set_container(container: ServiceContainer) -> None:
    """Set the global service container instance."""
    global _container
    with _container_lock:
        _container = container


# Decorator for automatic service registration
def injectable(
    service_type: Optional[Type] = None,
    lifecycle: ServiceLifecycle = ServiceLifecycle.TRANSIENT,
    container: Optional[ServiceContainer] = None,
) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator for automatic service registration.
    
    Args:
        service_type: Service interface type (defaults to decorated class)
        lifecycle: Service lifecycle mode
        container: Service container (defaults to global container)
        
    Returns:
        Decorated class with service registration
        
    Example:
        @injectable(IUserService, ServiceLifecycle.SINGLETON)
        class UserService:
            pass
    """
    def decorator(cls: Type[T]) -> Type[T]:
        target_container = container or get_container()
        target_service_type = service_type or cls
        
        # Register based on lifecycle
        if lifecycle == ServiceLifecycle.SINGLETON:
            target_container.register_singleton(target_service_type, cls)
        elif lifecycle == ServiceLifecycle.SCOPED:
            target_container.register_scoped(target_service_type, cls)
        else:
            target_container.register_transient(target_service_type, cls)
            
        logger.debug(f"Auto-registered service {target_service_type} -> {cls} with {lifecycle} lifecycle")
        return cls
    
    return decorator


# Convenience functions
def resolve(service_type: Type[T], container: Optional[ServiceContainer] = None) -> T:
    """Resolve a service from the container."""
    target_container = container or get_container()
    return target_container.resolve(service_type)


def register_singleton(
    service_type: Type[T], 
    implementation: Union[Type[T], T, Callable[..., T]], 
    container: Optional[ServiceContainer] = None
) -> None:
    """Register a singleton service."""
    target_container = container or get_container()
    target_container.register_singleton(service_type, implementation)


def register_transient(
    service_type: Type[T], 
    implementation: Union[Type[T], Callable[..., T]], 
    container: Optional[ServiceContainer] = None
) -> None:
    """Register a transient service."""
    target_container = container or get_container()
    target_container.register_transient(service_type, implementation)


def register_scoped(
    service_type: Type[T], 
    implementation: Union[Type[T], Callable[..., T]], 
    container: Optional[ServiceContainer] = None
) -> None:
    """Register a scoped service."""
    target_container = container or get_container()
    target_container.register_scoped(service_type, implementation)