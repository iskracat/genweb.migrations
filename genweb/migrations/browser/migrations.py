from five import grok
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot

from collective.transmogrifier.transmogrifier import Transmogrifier


class PloneorgMigrationMain(grok.View):
    grok.context(IPloneSiteRoot)
    grok.name('ploneorg_migration_main')

    def render(self):
        portal = api.portal.get()
        transmogrifier = Transmogrifier(portal)
        transmogrifier('plone.org.main')


class MigrationTest(grok.View):
    grok.context(IPloneSiteRoot)
    grok.name('migration_test')

    def render(self):
        portal = api.portal.get()
        transmogrifier = Transmogrifier(portal)
        transmogrifier('genweb.migrations.test')


class ExportDXTest(grok.View):
    grok.context(IPloneSiteRoot)
    grok.name('export_dx_test')

    def render(self):
        portal = api.portal.get()
        transmogrifier = Transmogrifier(portal)
        transmogrifier('genweb.migrations.dxexport.test')
