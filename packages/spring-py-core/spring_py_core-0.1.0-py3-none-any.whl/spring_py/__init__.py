"""
Spring-Py: A Python implementation of Spring Framework IoC container
"""

from .annotation import Component, Configuration, Bean, Autowired, Service
from .scanner import ComponentScanner, scan_components
from .container import Container, BeanInfo
from .context import ApplicationContext
from .global_context import (
    initialize_context, 
    get_context, 
    get_bean, 
    is_context_initialized
)
from .application import SpringApplication, SpringBootApplication

__version__ = "0.1.0"
__all__ = [
    "Component", "Configuration", "Bean", "Autowired", "Service",
    "ComponentScanner", "scan_components",
    "Container", "BeanInfo",
    "ApplicationContext",
    "initialize_context", "get_context", "get_bean", "is_context_initialized",
    "SpringApplication", "SpringBootApplication"
]
