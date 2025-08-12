# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.prepare_planned_failver_params

class PlannedFailoverParams2(object):

    """Implementation of the 'PlannedFailoverParams2' model.

    Specifies parameters to create a planned failover.

    Attributes:
        mtype (Type21Enum): Spcifies the planned failover type.<br> 'Prepare'
            indicates this is a preparation for failover.<br> 'Finalize'
            indicates this is finalization of failover. After this is done,
            the view can be used as source view.
        prepare_planned_failver_params (PreparePlannedFailverParams):
            Specifies parameters of preparation of a planned failover.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mtype":'type',
        "prepare_planned_failver_params":'preparePlannedFailverParams'
    }

    def __init__(self,
                 mtype=None,
                 prepare_planned_failver_params=None):
        """Constructor for the PlannedFailoverParams2 class"""

        # Initialize members of the class
        self.mtype = mtype
        self.prepare_planned_failver_params = prepare_planned_failver_params


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
        mtype = dictionary.get('type')
        prepare_planned_failver_params = cohesity_management_sdk.models_v2.prepare_planned_failver_params.PreparePlannedFailverParams.from_dictionary(dictionary.get('preparePlannedFailverParams')) if dictionary.get('preparePlannedFailverParams') else None

        # Return an object of this model
        return cls(mtype,
                   prepare_planned_failver_params)


