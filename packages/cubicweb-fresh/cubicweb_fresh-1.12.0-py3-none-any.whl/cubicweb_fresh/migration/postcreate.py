# -*- coding: utf-8 -*-
# postcreate script. You could setup a workflow here for example

for login in (
    "alf",
    "syt",
    "nico",
    "jphc",
    "ocy",
    "auc",
    "katia",
    "graz",
    "dede",
    "juj",
    "ludal",
    "steph",
    "arthur",
    "david",
    "joel",
    "gaston",
    "adim",
):
    rql(
        "INSERT CWUser E: E login %(login)s, E upassword %(login)s, E in_group G "
        'WHERE G name "users"',
        {"login": login},
    )
    rql(
        "INSERT PaidByAccount P: P label %(label)s, P associated_to U WHERE U login %(login)s",
        {"label": "refund account - %s" % login, "login": login},
    )
    rql(
        "INSERT PaidForAccount P: P label %(label)s",
        {"label": "charge account - %s" % login},
    )


for label in (
    "Logilab - CB Nicolas",
    "Logilab - CB Alexandre",
    "Logilab - CB Olivier",
    "Logilab - Espèces",
):
    rql("INSERT PaidByAccount P: P label %(label)s", {"label": label})
