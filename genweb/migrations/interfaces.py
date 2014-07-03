# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from zope.interface import Interface

from plone.theme.interfaces import IDefaultPloneLayer


class IGenwebMigrationsLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer."""


class ISerializer(Interface):
    def __call__(value, filestore, extra=None):
        """Convert to a serializable reprentation"""


class IDeserializer(Interface):
    def __call__(value, filestore, item):
        """Convert to a field value"""
