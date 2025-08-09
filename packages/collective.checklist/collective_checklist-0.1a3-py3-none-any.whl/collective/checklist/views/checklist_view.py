# -*- coding: utf-8 -*-

# from collective.checklist import _
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface

# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class IChecklistView(Interface):
    """Marker Interface for IChecklistView"""


@implementer(IChecklistView)
class ChecklistView(BrowserView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('checklist_view.pt')

    def __call__(self):
        # Implement your own actions:
        return self.index()
