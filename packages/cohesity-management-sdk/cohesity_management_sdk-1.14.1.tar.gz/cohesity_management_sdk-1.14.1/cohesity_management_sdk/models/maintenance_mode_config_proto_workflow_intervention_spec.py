# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class MaintenanceModeConfigProto_WorkflowInterventionSpec(object):

    """Implementation of the 'MaintenanceModeConfigProto_WorkflowInterventionSpec' model.

    Attributes:
        intervention (int): TODO: type description here.
        workflow_type (string): TODO: type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "intervention": 'intervention',
        "workflow_type": 'workflowType'
    }

    def __init__(self,
                 intervention=None,
                 workflow_type=None):
        """Constructor for the MaintenanceModeConfigProto_WorkflowInterventionSpec class"""

        # Initialize members of the class
        self.intervention = intervention
        self.workflow_type = workflow_type


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The interventions
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        intervention = dictionary.get('intervention')
        workflow_type = dictionary.get('workflowType')

        # Return an object of this model
        return cls(intervention,
                   workflow_type)


