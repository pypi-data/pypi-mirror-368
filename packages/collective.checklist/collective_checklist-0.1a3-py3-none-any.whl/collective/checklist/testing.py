# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.checklist


class CollectiveChecklistLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity

        self.loadZCML(package=plone.app.dexterity)
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=collective.checklist)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "collective.checklist:default")


COLLECTIVE_CHECKLIST_FIXTURE = CollectiveChecklistLayer()


COLLECTIVE_CHECKLIST_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_CHECKLIST_FIXTURE,),
    name="CollectiveChecklistLayer:IntegrationTesting",
)


COLLECTIVE_CHECKLIST_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_CHECKLIST_FIXTURE,),
    name="CollectiveChecklistLayer:FunctionalTesting",
)


COLLECTIVE_CHECKLIST_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_CHECKLIST_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="CollectiveChecklistLayer:AcceptanceTesting",
)
