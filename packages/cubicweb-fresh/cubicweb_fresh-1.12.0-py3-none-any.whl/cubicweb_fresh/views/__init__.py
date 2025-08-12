"""template-specific forms/views/actions/components"""

from cubicweb_web import formwidgets as fw
from cubicweb_web.views import uicfg
from cubicweb_web.views.ajaxcontroller import ajaxfunc

_afs = uicfg.autoform_section
_affk = uicfg.autoform_field_kwargs
_afs.tag_subject_of(("Expense", "spent_for", "*"), "main", "attributes")
_afs.tag_subject_of(("Expense", "spent_for", "*"), "muledit", "attributes")
_affk.tag_subject_of(
    ("Expense", "spent_for", "*"),
    {
        "widget": fw.LazyRestrictedAutoCompletionWidget(
            autocomplete_initfunc="get_concerned_by",
            autocomplete_settings={"limit": 100, "delay": 300},
        )
    },
)


@ajaxfunc(output_type="json")
def get_concerned_by(self):
    term = self._cw.form["q"]
    limit = self._cw.form.get("limit", 50)
    return [
        {"value": eid, "label": ref}
        for eid, ref in self._cw.execute(
            "DISTINCT Any W,R ORDERBY R LIMIT %s WHERE W ref R,"
            "W ref ILIKE %%(term)s" % limit,
            {"term": "%%%s%%" % term},
        )
    ]
