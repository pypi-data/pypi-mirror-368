from plone.app.z3cform.interfaces import ITextAreaWidget
from plone.app.z3cform.utils import dict_merge
from plone.app.z3cform.utils import get_portal_url
from plone.app.z3cform.widgets.text import TextAreaWidget
from plone.app.z3cform.widgets.datetime import get_date_options
from plone.app.z3cform.widgets.relateditems import get_relateditems_options
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.interface import implementer_only


# def get_checklist_options(context, querystring_view):
    # portal_url = get_portal_url(context)
    # try:
    #     base_url = context.absolute_url()
    # except AttributeError:
    #     base_url = portal_url
    # return {
    #     "indexOptionsUrl": f"{portal_url}/{querystring_view}",
    #     "previewURL": "%s/@@querybuilder_html_results" % base_url,
    #     "previewCountURL": "%s/@@querybuildernumberofresults" % base_url,
    #     "patternDateOptions": get_date_options(getRequest()),
    #     "patternAjaxSelectOptions": {"separator": ";"},
    #     "patternRelateditemsOptions": get_relateditems_options(
    #         context,
    #         None,
    #         ";",
    #         "plone.app.vocabularies.Catalog",
    #         "@@getVocabulary",
    #         "relatedItems",
    #         include_recently_added=False,
    #     ),
    # }


class IChecklistWidget(ITextAreaWidget):
    """
    """


@implementer_only(IChecklistWidget)
class ChecklistWidget(TextAreaWidget, Widget):
    """Checklist widget for z3c.form."""

    klass = "my-checklist-widget"

    def update(self):
        super().update()
        field = getattr(self, "field", None)


@implementer(IFieldWidget)
def ChecklistFieldWidget(field, request):
    return FieldWidget(field, ChecklistWidget(request))
