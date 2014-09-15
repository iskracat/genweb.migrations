# -*- coding: utf-8 -*-
"""Init and utils."""

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('genweb.migrations')

import logging

requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
