"""specific actions for fresh template

:organization: Logilab
:copyright: 2008-2024 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from cubicweb import _
from cubicweb.predicates import is_instance
from cubicweb_web.action import Action


class AccountingAction(Action):
    __regid__ = "accaction"
    __select__ = is_instance("Expense")
    title = _("generate accounting entries")

    def url(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        return entity.absolute_url(vid="accexpense")
