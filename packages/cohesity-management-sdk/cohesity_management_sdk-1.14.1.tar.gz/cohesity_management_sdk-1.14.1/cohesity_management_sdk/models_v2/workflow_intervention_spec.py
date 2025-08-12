# -*- coding: utf-8 -*-


class WorkflowInterventionSpec(object):

    """Implementation of the 'WorkflowInterventionSpec' model.

    Specifies the intervention for each workflow type.

    Attributes:
        intervention (InterventionEnum): Specifies the intervention type for ongoing tasks.
        workflow_type (WorkflowTypeEnum): Specifies the workflow type for which an intervention would be
          needed when maintenance mode begins

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "intervention":'intervention',
        "workflow_type":'workflowType'
    }

    def __init__(self,
                 intervention=None,
                 workflow_type=None):
        """Constructor for the WorkflowInterventionSpec class"""

        # Initialize members of the class
        self.intervention = intervention
        self.workflow_type = workflow_type


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
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