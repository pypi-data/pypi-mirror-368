# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s collective.checklist -t test_checklist.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src collective.checklist.testing.COLLECTIVE_CHECKLIST_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/collective/checklist/tests/robot/test_checklist.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a site administrator I can add a Checklist
  Given a logged-in site administrator
    and an add Checklist form
   When I type 'My Checklist' into the title field
    and I submit the form
   Then a Checklist with the title 'My Checklist' has been created

Scenario: As a site administrator I can view a Checklist
  Given a logged-in site administrator
    and a Checklist 'My Checklist'
   When I go to the Checklist view
   Then I can see the Checklist title 'My Checklist'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Checklist form
  Go To  ${PLONE_URL}/++add++Checklist

a Checklist 'My Checklist'
  Create content  type=Checklist  id=my-checklist  title=My Checklist

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Checklist view
  Go To  ${PLONE_URL}/my-checklist
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Checklist with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Checklist title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
