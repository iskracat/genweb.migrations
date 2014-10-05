from five import grok
from plone import api
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import IPloneSiteRoot

from genweb.controlpanel.interface import IGenwebControlPanelSettings

import json
import requests

PROPERTIES_MAP = {'titolespai_ca': 'html_title_ca',
                  'titolespai_es': 'html_title_es',
                  'titolespai_en': 'html_title_en',
                  'firmaunitat_ca': 'signatura_unitat_ca',
                  'firmaunitat_es': 'signatura_unitat_es',
                  'firmaunitat_en': 'signatura_unitat_en',
                  'contacteid': 'contacte_id',
                  'especific1': 'especific1',
                  'especific2': 'especific2',
                  'idestudiMaster': 'idestudi_master'}


class SetupMigration(grok.View):
    grok.context(IPloneSiteRoot)
    grok.name('setup_migration')
    grok.require('cmf.ManagePortal')

    def render(self):
        qi = api.portal.get_tool('portal_quickinstaller')
        qi.installProduct('pas.plugins.osiris')


class ExportGWConfig(grok.View):
    grok.context(IPloneSiteRoot)
    grok.name('export_gw_properties')
    grok.require('cmf.ManagePortal')

    def render(self):
        portal = api.portal.get()
        p_properties = portal.portal_properties
        properties_map = p_properties.genwebupc_properties.propertyMap()
        result = {}
        for gw_property in properties_map:
            result[gw_property['id']] = p_properties.genwebupc_properties.getProperty(gw_property['id'])

        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(result)


class ImportGWConfig(grok.View):
    grok.context(IPloneSiteRoot)
    grok.name('import_gw_properties')
    grok.require('cmf.ManagePortal')

    def update(self):
        self.registry = getUtility(IRegistry)
        self.gw_settings = self.registry.forInterface(IGenwebControlPanelSettings)

    def render(self):
        remote_server = 'http://127.0.0.1:9090'
        remote_path = '/ca1/ca1'
        remote_username = 'victor.fernandez'
        remote_token = 'uj5v4XrWMxGP25CN3pAE39mYCL7cwBMV'
        headers = {'X-Oauth-Username': remote_username,
                   'X-Oauth-Token': remote_token,
                   'X-Oauth-Scope': 'widgetcli',
                   }
        req = requests.get('{}{}/export_gw_properties'.format(remote_server, remote_path), headers=headers)
        properties = req.json()
        for prop in properties.keys():
            if prop in PROPERTIES_MAP.keys():
                self.map_gw_property(PROPERTIES_MAP[prop], properties[prop])

    def map_gw_property(self, prop, value):
        setattr(self.gw_settings, prop, value)
