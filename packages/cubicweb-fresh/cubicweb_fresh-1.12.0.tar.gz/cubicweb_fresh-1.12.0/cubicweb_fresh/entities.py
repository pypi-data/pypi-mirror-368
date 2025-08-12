"""this contains the template-specific entities' classes"""

from cubicweb_expense.entities import ExpenseLine as BaseExpenseLine


class ExpenseLine(BaseExpenseLine):
    @property
    def workcase(self):
        rql = "Any R WHERE E has_lines EL, EL eid %(el)s, E spent_for W, W ref R"
        rset = self._cw.execute(rql, {"el": self.eid})
        if rset:
            return rset[0][0]
        return None
