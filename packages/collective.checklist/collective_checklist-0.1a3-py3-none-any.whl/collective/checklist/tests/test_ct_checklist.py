# -*- coding: utf-8 -*-
from collective.checklist.content.checklist import IChecklist  # NOQA E501
from collective.checklist.testing import (  # noqa
    COLLECTIVE_CHECKLIST_INTEGRATION_TESTING,
)
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest


class ChecklistIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_CHECKLIST_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.parent = self.portal

    def test_ct_checklist_schema(self):
        fti = queryUtility(IDexterityFTI, name="Checklist")
        schema = fti.lookupSchema()
        self.assertEqual(IChecklist, schema)

    def test_ct_checklist_fti(self):
        fti = queryUtility(IDexterityFTI, name="Checklist")
        self.assertTrue(fti)

    def test_ct_checklist_factory(self):
        fti = queryUtility(IDexterityFTI, name="Checklist")
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IChecklist.providedBy(obj),
            "IChecklist not provided by {0}!".format(
                obj,
            ),
        )

    def test_ct_checklist_adding(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        obj = api.content.create(
            container=self.portal,
            type="Checklist",
            id="checklist",
        )

        self.assertTrue(
            IChecklist.providedBy(obj),
            "IChecklist not provided by {0}!".format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn("checklist", parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn("checklist", parent.objectIds())

    def test_ct_checklist_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        fti = queryUtility(IDexterityFTI, name="Checklist")
        self.assertTrue(fti.global_allow, "{0} is not globally addable!".format(fti.id))
