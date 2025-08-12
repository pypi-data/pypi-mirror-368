# -*- coding: utf-8 -*-


class GCPNativeProtectionGroupObjectParams(object):

    """Implementation of the 'GCP Native Protection Group Object Params.' model.

    Specifies the object parameters to create GCP Native Protection Group.

    Attributes:
        disk_exclusion_name_params (list of string): Specifies the paramaters to exclude disks attached to GCP VM
          instances. Here only the name of the disks are taken for exclusion.
        id (long|int): Specifies the id of the object.
        name (string): Specifies the name of the virtual machine.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "disk_exclusion_name_params":'diskExclusionNameParams',
        "id":'id',
        "name":'name'
    }

    def __init__(self,
                 disk_exclusion_name_params=None,
                 id=None,
                 name=None):
        """Constructor for the GCPNativeProtectionGroupObjectParams class"""

        # Initialize members of the class
        self.disk_exclusion_name_params = disk_exclusion_name_params
        self.id = id
        self.name = name


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
        disk_exclusion_name_params = dictionary.get('diskExclusionNameParams')
        id = dictionary.get('id')
        name = dictionary.get('name')

        # Return an object of this model
        return cls(disk_exclusion_name_params,
                   id,
                   name)