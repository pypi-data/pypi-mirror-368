# template's specific schema
from yams.buildobjs import RelationDefinition
from cubicweb.schema import RRQLExpression
from cubicweb_workcase.schema import Workcase


class Training(Workcase):
    __specializes_schema__ = True


class spent_for(RelationDefinition):
    subject = "Expense"
    object = "Workcase"
    cardinality = "?*"
    __permissions__ = {
        "read": ("managers", "users"),
        "add": ("managers", RRQLExpression('NOT (S in_state ST, ST name "accepted")')),
        "delete": (
            "managers",
            RRQLExpression('NOT (S in_state ST, ST name "accepted")'),
        ),
    }
