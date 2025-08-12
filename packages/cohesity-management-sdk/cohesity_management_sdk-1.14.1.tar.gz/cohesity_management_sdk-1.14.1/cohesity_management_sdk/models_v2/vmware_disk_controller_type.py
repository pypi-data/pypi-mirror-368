# -*- coding: utf-8 -*-


class VmwareDiskControllerType(object):

    """Implementation of the 'VMware disk controller type.' model.

    Vmware disk controller type.

    Attributes:
        vmware_disk_controller_type (VmwareDiskControllerType1Enum): Specifies
            VMware disk controller type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "vmware_disk_controller_type":'vmwareDiskControllerType'
    }

    def __init__(self,
                 vmware_disk_controller_type=None):
        """Constructor for the VmwareDiskControllerType class"""

        # Initialize members of the class
        self.vmware_disk_controller_type = vmware_disk_controller_type


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
        vmware_disk_controller_type = dictionary.get('vmwareDiskControllerType')

        # Return an object of this model
        return cls(vmware_disk_controller_type)


