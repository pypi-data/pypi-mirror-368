# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.vmware_app_protection_parameters

class ActionsOnVmwareObjects(object):

    """Implementation of the 'Actions on VMware Objects' model.

    Specifies the parameters to perform an action on VMware Objects.

    Attributes:
        action (Action3Enum): Specifies the action on the Object.
        enable_app_protection_params (VmwareAppProtectionParameters):
            Specifies the parameters to enable app protection on VMware.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "action":'action',
        "enable_app_protection_params":'enableAppProtectionParams'
    }

    def __init__(self,
                 action=None,
                 enable_app_protection_params=None):
        """Constructor for the ActionsOnVmwareObjects class"""

        # Initialize members of the class
        self.action = action
        self.enable_app_protection_params = enable_app_protection_params


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
        action = dictionary.get('action')
        enable_app_protection_params = cohesity_management_sdk.models_v2.vmware_app_protection_parameters.VmwareAppProtectionParameters.from_dictionary(dictionary.get('enableAppProtectionParams')) if dictionary.get('enableAppProtectionParams') else None

        # Return an object of this model
        return cls(action,
                   enable_app_protection_params)


