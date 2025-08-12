# -*- coding: utf-8 -*-


class ActionsOnVmwareObjects1(object):

    """Implementation of the 'Actions on VMware objects.1' model.

    Actions on VMware objects.

    Attributes:
        vmware_object_action (VmwareObjectActionEnum): Specifies the actions
            on vmware objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "vmware_object_action":'vmwareObjectAction'
    }

    def __init__(self,
                 vmware_object_action=None):
        """Constructor for the ActionsOnVmwareObjects1 class"""

        # Initialize members of the class
        self.vmware_object_action = vmware_object_action


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
        vmware_object_action = dictionary.get('vmwareObjectAction')

        # Return an object of this model
        return cls(vmware_object_action)


