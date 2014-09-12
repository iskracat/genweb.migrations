from five import grok
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot

from collective.transmogrifier.transmogrifier import Transmogrifier


class SetupMigration(grok.View):
    grok.context(IPloneSiteRoot)
    grok.name('setup_migration')

    def render(self):
        qi = api.portal.get_tool('portal_quickinstaller')
        qi.installProduct('pas.plugins.osiris')
