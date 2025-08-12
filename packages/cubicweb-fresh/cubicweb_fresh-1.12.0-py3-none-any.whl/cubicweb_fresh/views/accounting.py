"""accounting views for fresh template

:organization: Logilab
:copyright: 2008-2024 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"


from logilab.mtconverter import xml_escape

from cubicweb import _
from cubicweb.predicates import is_instance
from cubicweb_web.view import EntityView


class ExpenseAccountingXmlView(EntityView):
    __regid__ = "accexpense"
    __select__ = is_instance("Expense")

    title = _("accounting entry view")
    templatable = False
    content_type = "text/xml"

    def call(self):
        """display a list of entities by calling their <item_vid> view"""
        self.w('<?xml version="1.0" encoding="%s"?>\n' % self._cw.encoding)
        self.w(
            '<?xml-stylesheet href="%saccounting-entries.xsl" '
            'rel="stylesheet" type="text/xsl"?>\n' % self._cw.datadir_url
        )
        self.w("<ecritures>\n")
        for i in range(self.cw_rset.rowcount):
            self.cell_call(i, 0)
        self.w("</ecritures>\n")

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        rset = entity.related("has_lines")
        for i in range(len(rset)):
            self.wview("accentry", rset, row=i, col=0)


class ExpenseLineAccountingEntryXmlView(EntityView):
    __regid__ = "accentry"
    __select__ = is_instance(
        "ExpenseLine",
    )

    title = _("accounting entry view")
    templatable = False
    content_type = "text/xml"

    def call(self):
        """display a list of entities by calling their <item_vid> view"""
        self.w('<?xml version="1.0" encoding="%s"?>\n' % self._cw.encoding)
        self.w(
            '<?xml-stylesheet href="%saccounting-entries.xsl" '
            'rel="stylesheet" type="text/xsl"?>\n' % self._cw.datadir_url
        )
        self.w("<ecritures>\n")
        for i in range(self.cw_rset.rowcount):
            self.cell_call(i, 0)
        self.w("</ecritures>\n")

    def cell_call(self, row, col):
        entity = self.cw_rset.complete_entity(row, col)
        self.w('  <ecriture date="%s">\n' % entity.diem.strftime("%Y-%m-%d"))
        self.w("    <libelle>%s</libelle>\n" % xml_escape(entity.dc_long_title()))
        amount = round(entity.euro_amount(), 2)
        taxes = round(entity.taxes, 2)
        account = (
            entity.paid_by[0].account and xml_escape(entity.paid_by[0].account) or ""
        )
        self.w('    <credit compte="%s" montant="%.2f" />\n' % (account, amount))
        if entity.taxes:
            # XXX hardcoded account for VAT
            self.w('    <debit compte="44566" montant="%.2f" />\n' % entity.taxes)
        taxfree = int(round((amount - taxes) * 100))
        accounts = list(entity.paid_for)
        debit_quotient = taxfree / len(accounts)
        debit_remainder = taxfree % len(accounts)
        for account in accounts:
            if debit_remainder > 0:
                debit = (debit_quotient + 1) / 100.0
                debit_remainder -= 1
            else:
                debit = debit_quotient / 100.0
            account = account.account and xml_escape(account.account) or ""
            self.w('    <debit compte="%s" montant="%.2f" />\n' % (account, debit))
        if entity.workcase:
            self.w("    <groupe>%s</groupe>\n" % xml_escape(entity.workcase))
        self.w("  </ecriture>\n")
