# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.vcd_additional_params

class VmwareAdditionalParams(object):

    """Implementation of the 'VMware Additional Params.' model.

    Additional params for VMware protection source.

    Attributes:
        vcd_params (VCDAdditionalParams): Additional params for VCD protection
            source.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "vcd_params":'vcdParams'
    }

    def __init__(self,
                 vcd_params=None):
        """Constructor for the VmwareAdditionalParams class"""

        # Initialize members of the class
        self.vcd_params = vcd_params


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
        vcd_params = cohesity_management_sdk.models_v2.vcd_additional_params.VCDAdditionalParams.from_dictionary(dictionary.get('vcdParams')) if dictionary.get('vcdParams') else None

        # Return an object of this model
        return cls(vcd_params)


