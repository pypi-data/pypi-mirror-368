# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.failover

class GetViewFailoverResponseBody(object):

    """Implementation of the 'GetViewFailoverResponseBody' model.

    Specifies planned failovers and unplanned failovers of a view.

    Attributes:
        failovers (list of Failover): Specifies a list of failovers.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "failovers":'failovers'
    }

    def __init__(self,
                 failovers=None):
        """Constructor for the GetViewFailoverResponseBody class"""

        # Initialize members of the class
        self.failovers = failovers


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
        failovers = None
        if dictionary.get("failovers") is not None:
            failovers = list()
            for structure in dictionary.get('failovers'):
                failovers.append(cohesity_management_sdk.models_v2.failover.Failover.from_dictionary(structure))

        # Return an object of this model
        return cls(failovers)


