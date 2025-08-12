if "Training" not in schema:
    add_entity_type("Training")

# workflows doen't understand yams inheritance
rql(
    "SET WF workflow_of ET, ET default_workflow WF "
    'WHERE WF workflow_of WC, WC name "Workcase", ET name "Training"'
)
commit()
