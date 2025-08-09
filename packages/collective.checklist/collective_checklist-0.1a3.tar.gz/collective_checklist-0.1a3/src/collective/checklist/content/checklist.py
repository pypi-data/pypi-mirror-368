# -*- coding: utf-8 -*-
from collective.checklist import _
from collective.checklist.widgets.checklist import ChecklistFieldWidget
from plone import schema
from plone.autoform import directives
from plone.dexterity.content import Item
from plone.supermodel import model
from zope.interface import implementer

import json


class IChecklist(model.Schema):
    """Marker interface and Dexterity Python Schema for Checklist"""

    directives.widget(checklist=ChecklistFieldWidget)
    checklist = schema.JSONField(
        title=_(
            "Checklist",
        ),
        schema=json.dumps({}),
        default={"schema": [], "data": "undefined"},
        required=False,
        readonly=False,
    )


@implementer(IChecklist)
class Checklist(Item):
    """Content-type class for IChecklist"""
