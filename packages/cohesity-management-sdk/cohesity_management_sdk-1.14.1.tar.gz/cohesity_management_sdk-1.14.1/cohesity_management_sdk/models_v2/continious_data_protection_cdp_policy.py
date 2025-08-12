# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.cdp_retention

class ContiniousDataProtectionCDPPolicy(object):

    """Implementation of the 'Continious Data Protection (CDP) Policy.' model.

    Specifies CDP (Continious Data Protection) backup settings for a
    Protection Group.

    Attributes:
        retention (CdpRetention): Specifies the retention of a CDP backup.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "retention":'retention'
    }

    def __init__(self,
                 retention=None):
        """Constructor for the ContiniousDataProtectionCDPPolicy class"""

        # Initialize members of the class
        self.retention = retention


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
        retention = cohesity_management_sdk.models_v2.cdp_retention.CdpRetention.from_dictionary(dictionary.get('retention')) if dictionary.get('retention') else None

        # Return an object of this model
        return cls(retention)


