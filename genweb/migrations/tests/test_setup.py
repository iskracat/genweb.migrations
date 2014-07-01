# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from genweb.migrations.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of genweb.migrations into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if genweb.migrations is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('genweb.migrations'))

    def test_uninstall(self):
        """Test if genweb.migrations is cleanly uninstalled."""
        self.installer.uninstallProducts(['genweb.migrations'])
        self.assertFalse(self.installer.isProductInstalled('genweb.migrations'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that IGenwebMigrationsLayer is registered."""
        from genweb.migrations.interfaces import IGenwebMigrationsLayer
        from plone.browserlayer import utils
        self.failUnless(IGenwebMigrationsLayer in utils.registered_layers())
