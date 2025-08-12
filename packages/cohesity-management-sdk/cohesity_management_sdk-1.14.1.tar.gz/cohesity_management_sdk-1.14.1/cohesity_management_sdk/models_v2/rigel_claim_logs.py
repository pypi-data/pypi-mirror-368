# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.rigel_claim_log

class RigelClaimLogs(object):

    """Implementation of the 'Rigel Claim Logs.' model.

    Specifies the Rigel claim logs.

    Attributes:
        rigel_claim_logs (list of RigelClaimLog): Specifies Rigel claim logs.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "rigel_claim_logs":'rigelClaimLogs'
    }

    def __init__(self,
                 rigel_claim_logs=None):
        """Constructor for the RigelClaimLogs class"""

        # Initialize members of the class
        self.rigel_claim_logs = rigel_claim_logs


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
        rigel_claim_logs = None
        if dictionary.get("rigelClaimLogs") is not None:
            rigel_claim_logs = list()
            for structure in dictionary.get('rigelClaimLogs'):
                rigel_claim_logs.append(cohesity_management_sdk.models_v2.rigel_claim_log.RigelClaimLog.from_dictionary(structure))

        # Return an object of this model
        return cls(rigel_claim_logs)


