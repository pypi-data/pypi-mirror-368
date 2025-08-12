# -*- coding: utf-8 -*-


class VmwareSourceType(object):

    """Implementation of the 'VMware Source Type' model.

    VMware Source Type

    Attributes:
        vmware_source_type (VmwareSourceType1Enum): Specifies the VMware
            Source types.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "vmware_source_type":'vmwareSourceType'
    }

    def __init__(self,
                 vmware_source_type=None):
        """Constructor for the VmwareSourceType class"""

        # Initialize members of the class
        self.vmware_source_type = vmware_source_type


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
        vmware_source_type = dictionary.get('vmwareSourceType')

        # Return an object of this model
        return cls(vmware_source_type)


