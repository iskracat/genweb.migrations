from zope.interface import implements
from zope.interface import classProvides
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.utils import Matcher
from collective.transmogrifier.utils import defaultKeys
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.interfaces import IBaseObject
from DateTime import DateTime

from plone.dexterity.interfaces import IDexterityContent

from zope.interface import classProvides, implements
from zope.schema import getFieldsInOrder
from collective.transmogrifier.interfaces import ISectionBlueprint, ISection
from Products.Archetypes.interfaces import IBaseObject
from genweb.migrations.interfaces import IDeserializer

import base64
import pprint


class PrettyPrinter(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.pprint = pprint.PrettyPrinter().pprint

    def __iter__(self):
        def undict(source):
            """ Recurse through the structure and convert dictionaries
                into sorted lists
            """
            res = list()
            if type(source) is dict:
                source = sorted(source.items())
            if type(source) in (list, tuple):
                for item in source:
                    res.append(undict(item))
            else:
                res = source
            # convert a tuple into tuple back
            if type(source) is tuple:
                res = tuple(res)
            return res

        for item in self.previous:
            self.pprint(undict(item))
            yield item


class DataFields(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.datafield_prefix = options.get('datafield-prefix', '_datafield_')
        self.root_path_length = len(self.context.getPhysicalPath())

    def __iter__(self):
        for item in self.previous:

            # not enough info
            if '_path' not in item:
                yield item
                continue

            obj = self.context.unrestrictedTraverse(item['_path'].lstrip('/'), None)

            # path doesn't exist
            if obj is None:
                yield item
                continue

            # do nothing if we got a wrong object through acquisition
            path = item['_path']
            if path.startswith('/'):
                path = path[1:]
            if '/'.join(obj.getPhysicalPath()[self.root_path_length:]) != path:
                yield item
                continue

            for key in item.keys():

                if not key.startswith(self.datafield_prefix):
                    continue

                fieldname = key[len(self.datafield_prefix):]

                if IBaseObject.providedBy(obj):

                    field = obj.getField(fieldname)
                    if field is None:
                        continue
                    value = base64.b64decode(item[key]['data'])

                    # XXX: handle other data field implementations
                    old_value = field.get(obj).data
                    if value != old_value:
                        field.set(obj, value)
                        obj.setFilename(item[key]['filename'])
                        obj.setContentType(item[key]['content_type'])
                else:
                    for name, fieldd in getFieldsInOrder(obj.getTypeInfo().lookupSchema()):
                        if name == fieldname:
                            field = fieldd

                    deserializer = IDeserializer(field)
                    value = deserializer(item[key], None, item)
                    field.set(field.interface(obj), value)

            yield item


class WorkflowHistory(object):
    """
    """
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.name = name
        self.options = options
        self.previous = previous
        self.context = transmogrifier.context
        self.wftool = getToolByName(self.context, 'portal_workflow')

        if 'path-key' in options:
            pathkeys = options['path-key'].splitlines()
        else:
            pathkeys = defaultKeys(options['blueprint'], name, 'path')
        self.pathkey = Matcher(*pathkeys)

        if 'workflowhistory-key' in options:
            workflowhistorykeys = options['workflowhistory-key'].splitlines()
        else:
            workflowhistorykeys = defaultKeys(options['blueprint'], name, 'workflow_history')
        self.workflowhistorykey = Matcher(*workflowhistorykeys)


    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]
            workflowhistorykey = self.workflowhistorykey(*item.keys())[0]

            if not pathkey or not workflowhistorykey or \
               workflowhistorykey not in item:  # not enough info
                yield item; continue

            obj = self.context.unrestrictedTraverse(item[pathkey].lstrip('/'), None)
            if obj is None or not getattr(obj, 'workflow_history', False):
                yield item; continue

            import ipdb;ipdb.set_trace()
            if IBaseObject.providedBy(obj) or IDexterityContent.providedBy(obj):
                item_tmp = item

                # get back datetime stamp and set the workflow history
                for workflow in item_tmp[workflowhistorykey]:
                    for k, workflow2 in enumerate(item_tmp[workflowhistorykey][workflow]):
                        if 'time' in item_tmp[workflowhistorykey][workflow][k]:
                            item_tmp[workflowhistorykey][workflow][k]['time'] = DateTime(
                                    item_tmp[workflowhistorykey][workflow][k]['time'])
                obj.workflow_history.data = item_tmp[workflowhistorykey]

                # update security
                workflows = self.wftool.getWorkflowsFor(obj)
                if workflows:
                    workflows[0].updateRoleMappingsFor(obj)

            yield item
