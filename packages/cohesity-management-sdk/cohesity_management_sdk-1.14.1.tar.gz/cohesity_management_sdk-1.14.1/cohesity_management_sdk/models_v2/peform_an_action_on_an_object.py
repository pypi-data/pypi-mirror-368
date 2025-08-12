# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.actions_on_vmware_objects

class PeformAnActionOnAnObject(object):

    """Implementation of the 'Peform an action on an Object.' model.

    Specifies the request to peform an action on an Object.

    Attributes:
        environment (Environment4Enum): Specifies the environment type of the
            Object.
        vmware_params (ActionsOnVmwareObjects): Specifies the parameters to
            perform an action on VMware Objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "environment":'environment',
        "vmware_params":'vmwareParams'
    }

    def __init__(self,
                 environment=None,
                 vmware_params=None):
        """Constructor for the PeformAnActionOnAnObject class"""

        # Initialize members of the class
        self.environment = environment
        self.vmware_params = vmware_params


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
        environment = dictionary.get('environment')
        vmware_params = cohesity_management_sdk.models_v2.actions_on_vmware_objects.ActionsOnVmwareObjects.from_dictionary(dictionary.get('vmwareParams')) if dictionary.get('vmwareParams') else None

        # Return an object of this model
        return cls(environment,
                   vmware_params)


